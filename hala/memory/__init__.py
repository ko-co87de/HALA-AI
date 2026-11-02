"""Memory system with fact/inference/source/experience separation.

Design based on HINDSIGHT (arXiv 2025) and MemOS (SJTU/ZJU, 2025).
"""
from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Optional

from hala.types import FactConfidence, MemoryRecord


class MemoryStore:
    """In-memory store with confidence-tiered records."""

    def __init__(self):
        self._records: list[MemoryRecord] = []
        self._by_type: dict[str, list[MemoryRecord]] = defaultdict(list)
        self._by_confidence: dict[FactConfidence, list[MemoryRecord]] = defaultdict(list)

    def add(self, record: MemoryRecord) -> str:
        self._records.append(record)
        self._by_type[record.type].append(record)
        self._by_confidence[record.confidence].append(record)
        return record.id

    def add_fact(self, content: str, source: Optional[str] = None,
                 confidence: FactConfidence = FactConfidence.VERIFIED) -> str:
        return self.add(MemoryRecord(
            type="fact", content=content, source=source, confidence=confidence
        ))

    def add_inference(self, content: str, source: str = "model",
                      confidence: FactConfidence = FactConfidence.INFERRED) -> str:
        return self.add(MemoryRecord(
            type="inference", content=content, source=source, confidence=confidence
        ))

    def add_experience(self, content: str, outcome: str,
                       source: str = "agent") -> str:
        return self.add(MemoryRecord(
            type="experience", content=content,
            source=source,
            metadata={"outcome": outcome},
        ))

    def add_source(self, content: str, url: str,
                   retrieved_at: Optional[float] = None) -> str:
        return self.add(MemoryRecord(
            type="source", content=content, source=url,
            timestamp=retrieved_at or time.time(),
        ))

    def search(self, query: str, limit: int = 10,
               types: Optional[list[str]] = None,
               min_confidence: Optional[FactConfidence] = None) -> list[MemoryRecord]:
        """Keyword-based search with confidence and type filtering."""
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return []

        rank_order = {
            FactConfidence.VERIFIED: 3,
            FactConfidence.INFERRED: 2,
            FactConfidence.UNCONFIRMED: 1,
        }

        scored: list[tuple[int, MemoryRecord]] = []
        for rec in self._records:
            if types and rec.type not in types:
                continue
            if min_confidence and rank_order[rec.confidence] < rank_order[min_confidence]:
                continue
            rec_words = set(re.findall(r"\w+", rec.content.lower()))
            overlap = len(query_words & rec_words)
            if overlap > 0:
                score = overlap * 10 + rank_order[rec.confidence]
                scored.append((score, rec))

        scored.sort(key=lambda x: (-x[0], x[1].timestamp))
        return [rec for _, rec in scored[:limit]]

    def get_by_type(self, type_: str, limit: int = 20) -> list[MemoryRecord]:
        return self._by_type.get(type_, [])[-limit:]

    def get_verified_facts(self, limit: int = 20) -> list[MemoryRecord]:
        return self._by_confidence.get(FactConfidence.VERIFIED, [])[-limit:]

    def clear(self) -> None:
        self._records.clear()
        self._by_type.clear()
        self._by_confidence.clear()

    def __len__(self) -> int:
        return len(self._records)

    def stats(self) -> dict[str, int]:
        return {t: len(recs) for t, recs in self._by_type.items()}


class ConversationMemory:
    """Short-term conversation context with bounded history."""

    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: list = []

    def add(self, message) -> None:
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            # Keep system message, drop oldest non-system
            system = [m for m in self.messages if m.role.value == "system"]
            rest = [m for m in self.messages if m.role.value != "system"]
            self.messages = system + rest[-(self.max_messages - len(system)):]

    def clear(self) -> None:
        self.messages.clear()

    def to_list(self) -> list:
        return list(self.messages)


class LongTermMemory:
    """Persistent knowledge and experience store."""

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    def remember(self, content: str, type_: str = "fact",
                 source: Optional[str] = None,
                 confidence: FactConfidence = FactConfidence.VERIFIED) -> str:
        rec = MemoryRecord(type=type_, content=content, source=source,
                           confidence=confidence)
        return self.store.add(rec)

    def recall(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        return self.store.search(query, limit=limit)

    def stats(self) -> dict[str, int]:
        return self.store.stats()