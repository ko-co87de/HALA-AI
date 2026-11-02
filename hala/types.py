"""Shared types and contracts for HALA AI."""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    OBSERVATION = "observation"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool: str
    arguments: dict[str, Any]
    thought: Optional[str] = None


class ToolResult(BaseModel):
    tool_call_id: str
    tool: str
    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0


class FactConfidence(str, Enum):
    VERIFIED = "verified"       # confirmed by code, test, or authoritative source
    INFERRED = "inferred"       # model-derived, confidence-scored
    UNCONFIRMED = "unconfirmed" # external claim, not yet verified


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str                     # fact | inference | experience | source
    content: str
    confidence: FactConfidence = FactConfidence.UNCONFIRMED
    source: Optional[str] = None  # provenance: url, file, or model name
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    subtasks: list[str] = Field(default_factory=list)
    assigned_agent: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    task_id: str
    agent: str
    success: bool
    output: str
    error: Optional[str] = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    duration_ms: float = 0.0
    confidence: FactConfidence = FactConfidence.INFERRED