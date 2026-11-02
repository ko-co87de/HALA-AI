"""Reasoning engine: structured reasoning steps."""
from __future__ import annotations

from typing import Any

from hala.models import ModelRouter
from hala.types import Message, MessageRole


def reason(router: ModelRouter, question: str, context: str = "",
           max_tokens: int = 512) -> str:
    """Produce a reasoned answer using chain-of-thought."""
    system = Message(
        role=MessageRole.SYSTEM,
        content=(
            "You are a careful reasoner. Think step by step. "
            "Show your reasoning, then give a final concise answer. "
            "If unsure, say so. Never fabricate facts."
        ),
    )
    user = Message(
        role=MessageRole.USER,
        content=f"Context: {context}\n\nQuestion: {question}" if context
        else f"Question: {question}",
    )
    return router.complete([system, user], max_tokens=max_tokens, temperature=0.0)


def reason_math(router: ModelRouter, problem: str, max_tokens: int = 512) -> str:
    """Reason about a math problem step by step."""
    system = Message(
        role=MessageRole.SYSTEM,
        content=(
            "You are a mathematician. Solve step by step. "
            "Show each step clearly. End with the final answer on its own line "
            "prefixed with 'ANSWER:'."
        ),
    )
    user = Message(role=MessageRole.USER, content=problem)
    return router.complete([system, user], max_tokens=max_tokens, temperature=0.0)