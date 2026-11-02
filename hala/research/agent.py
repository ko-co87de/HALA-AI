"""Research agent: independent scientific researcher."""
from __future__ import annotations

import re
from typing import Any

from hala.models import ModelRouter
from hala.types import AgentResult, Message, MessageRole, Task


class ResearchAgent:
    """Conducts research: web search, paper reading, repo analysis, reports."""

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter(preferred="hala-local-1.5b")

    def research(self, query: str, max_sources: int = 5) -> AgentResult:
        """Research a topic and produce a cited summary."""
        # Step 1: Search the web
        search_results = self._web_search(query, max_sources)

        # Step 2: Analyze and summarize
        system = Message(
            role=MessageRole.SYSTEM,
            content=(
                "You are a research analyst. Summarize the search results "
                "with citations. Note what is confirmed vs uncertain. "
                "End with 'SOURCES:' followed by the URLs."
            ),
        )
        user = Message(
            role=MessageRole.USER,
            content=f"Query: {query}\n\nSearch results:\n{search_results}",
        )
        summary = self.router.complete([system, user], max_tokens=1024, temperature=0.0)

        sources = re.findall(r"https?://\S+", summary)
        return AgentResult(
            task_id="", agent="researcher", success=True, output=summary,
        )

    def _web_search(self, query: str, max_results: int = 5) -> str:
        """Perform a web search and return formatted results."""
        try:
            import httpx
            url = "https://html.duckduckgo.com/html/"
            resp = httpx.post(url, data={"q": query}, timeout=30)
            results = re.findall(
                r'result__a"[^>]*>(.*?)</a>', resp.text, re.DOTALL
            )
            snippets = re.findall(
                r'class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.DOTALL
            )
            lines = []
            for i, (title, snippet) in enumerate(
                zip(results[:max_results], snippets[:max_results]), 1
            ):
                clean_title = re.sub(r"<[^>]+>", "", title).strip()
                clean_snippet = re.sub(r"<[^>]+>", "", snippet).strip()
                lines.append(f"{i}. {clean_title}\n   {clean_snippet}")
            return "\n\n".join(lines) if lines else "No results found."
        except Exception as exc:
            return f"[Web search failed: {exc}]"

    def analyze_repo(self, repo_url: str) -> AgentResult:
        """Analyze a GitHub repository structure and purpose."""
        system = Message(
            role=MessageRole.SYSTEM,
            content=(
                "You are a code analyst. Given a repository URL, describe: "
                "1. What it does. 2. Key architecture. 3. License. "
                "4. Pros and cons. 5. Reuse potential."
            ),
        )
        user = Message(role=MessageRole.USER, content=f"Repository: {repo_url}")
        analysis = self.router.complete([system, user], max_tokens=1024, temperature=0.0)
        return AgentResult(task_id="", agent="researcher",
                           success=True, output=analysis)