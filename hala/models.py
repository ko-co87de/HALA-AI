"""Model registry, adapters, inference, and routing.

Provider-independent design. Default local engine is llama.cpp.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from hala.types import Message


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def _resolve_path(path: str) -> str:
    """Resolve a model path. Tries absolute, CWD-relative, and HALA_DATA."""
    p = Path(path)
    if p.is_absolute() and p.exists():
        return str(p)
    candidates = [
        Path.cwd() / path,
        Path(os.environ.get("HALA_DATA", "")) / path,
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    # Return CWD-relative path; adapter will report a clear error
    return str(Path.cwd() / path)


class ModelConfig(BaseModel):
    name: str
    provider: str            # llama.cpp | openai | anthropic | ollama
    path: Optional[str] = None  # local file path for GGUF
    endpoint: Optional[str] = None
    api_key_env: Optional[str] = None
    context_size: int = 4096
    max_tokens: int = 1024
    temperature: float = 0.0


# Default model registry. All are open-weight.
MODEL_REGISTRY: dict[str, ModelConfig] = {
    "hala-local-1.5b": ModelConfig(
        name="Qwen2.5-Coder-1.5B-Q4_K_M",
        provider="llama.cpp",
        path="models/qwen2.5-coder-1.5b-q4_k_m.gguf",
        context_size=32768,
        max_tokens=1024,
        temperature=0.0,
    ),
    "hala-primary": ModelConfig(
        name="Qwen3-235B-A22B",
        provider="openai",
        endpoint="https://dashscope.aliyuncs.com/api/v1",
        api_key_env="DASHSCOPE_API_KEY",
        context_size=33000,
        max_tokens=4096,
        temperature=0.0,
    ),
    "hala-fallback": ModelConfig(
        name="DeepSeek-V3",
        provider="openai",
        endpoint="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
        context_size=130000,
        max_tokens=4096,
        temperature=0.0,
    ),
}


class LlamaCppAdapter:
    """Local inference via llama.cpp binary."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.config.path = _resolve_path(config.path) if config.path else config.path
        self.binary = self._find_binary()

    def _find_binary(self) -> str:
        for name in ("llama-cli", "llama"):
            path = _which(name)
            if path:
                return path
        raise RuntimeError(
            "No llama.cpp binary found. Install llama.cpp or set LLAMA_CPP_BIN."
        )

    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        prompt = self._format_messages(messages)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        temperature = kwargs.get("temperature", self.config.temperature)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt)
            prompt_path = f.name

        try:
            cmd = [
                self.binary,
                "-m", self.config.path,
                "-f", prompt_path,
                "-n", str(max_tokens),
                "--temp", str(temperature),
                "-c", str(self.config.context_size),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
                cwd=Path(__file__).resolve().parent.parent,
            )
            output = result.stdout
            # Extract the response after the prompt marker
            marker = prompt.strip().split("\n")[-1]
            if marker in output:
                output = output.split(marker, 1)[1].strip()
            # Strip trailing interactive prompt
            for sep in ("\n> ", "\n\n> "):
                if sep in output:
                    output = output.split(sep, 1)[0].strip()
            return output
        finally:
            os.unlink(prompt_path)

    def _format_messages(self, messages: list[Message]) -> str:
        parts = []
        for m in messages:
            parts.append(f"{m.role.value}: {m.content}")
        parts.append("assistant:")
        return "\n".join(parts) + "\n"


class OpenAICompatibleAdapter:
    """Cloud inference via OpenAI-compatible API."""

    def __init__(self, config: ModelConfig):
        self.config = config

    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        import httpx

        api_key = os.environ.get(self.config.api_key_env or "", "")
        if not api_key:
            raise RuntimeError(
                f"Missing API key env var: {self.config.api_key_env}"
            )

        payload = {
            "model": self.config.name,
            "messages": [
                {"role": m.role.value, "content": m.content} for m in messages
            ],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        with httpx.Client(timeout=300) as client:
            resp = client.post(
                f"{self.config.endpoint}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


def shutil_which(name: str) -> Optional[str]:
    import shutil

    return shutil.which(name)


class ModelRouter:
    """Routes inference to the best available model with fallback."""

    def __init__(self, preferred: str = "hala-local-1.5b"):
        self.preferred = preferred
        self._adapters: dict[str, Any] = {}
        self._failed: set[str] = set()

    def _get_adapter(self, name: str):
        if name in self._adapters:
            return self._adapters[name]
        config = MODEL_REGISTRY.get(name)
        if not config:
            raise ValueError(f"Unknown model: {name}")
        if config.provider == "llama.cpp":
            adapter = LlamaCppAdapter(config)
        elif config.provider == "openai":
            adapter = OpenAICompatibleAdapter(config)
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
        self._adapters[name] = adapter
        return adapter

    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        """Try preferred model, then fallbacks. Skip known-failed cloud models."""
        order = [self.preferred]
        for name in MODEL_REGISTRY:
            if name not in order:
                order.append(name)

        last_error = None
        for name in order:
            if name in self._failed:
                continue
            try:
                adapter = self._get_adapter(name)
                result = adapter.complete(messages, **kwargs)
                return result
            except Exception as exc:
                last_error = exc
                self._failed.add(name)
                continue

        raise RuntimeError(f"All models failed. Last error: {last_error}")

    def mark_failed(self, name: str) -> None:
        self._failed.add(name)

    def reset_failures(self) -> None:
        self._failed.clear()