"""Shared data schemas for all riskqa modules."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class SeverityLevel(str, Enum):
    """Violation severity levels used across all modules."""
    info = "info"
    warning = "warning"
    critical = "critical"


class RiskLevel(str, Enum):
    """Overall risk assessment level."""
    safe = "safe"
    warning = "warning"
    violation = "violation"


class UrgencyLevel(str, Enum):
    """Work order urgency classification."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class ViolationDegree(str, Enum):
    """Violation ticket severity degree."""
    minor = "minor"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


# --- Common Models ---


class Violation(BaseModel):
    """A single detected violation entry."""
    type: str
    description: str
    severity: SeverityLevel
    evidence: str
    position: tuple[int, int] = (0, 0)


class Rule(BaseModel):
    """A rule for the rule engine (keyword or regex pattern)."""
    name: str
    pattern: str | list[str]
    category: str
    severity: SeverityLevel


class RuleMatch(BaseModel):
    """A match result from the rule engine."""
    rule_name: str
    matched_text: str
    position: tuple[int, int]
    severity: SeverityLevel


# --- CallQA Models ---


class CallFragment(BaseModel):
    """A single fragment in a call transcript."""
    speaker: Literal["agent", "customer"]
    start_time: float
    end_time: float
    text: str


class CallTranscript(BaseModel):
    """Full transcript of a phone call."""
    call_id: str
    duration_seconds: int
    fragments: list[CallFragment]


class CallQAReport(BaseModel):
    """Output report from call quality inspection."""
    call_id: str
    compliance_score: float
    risk_level: RiskLevel
    violations: list[Violation]
    quality_tags: list[str]
    summary: str


# --- ChatQA Models ---


class ChatMessage(BaseModel):
    """A single message in a chat session."""
    sender: Literal["agent", "customer"]
    timestamp: datetime
    content: str
    msg_type: Literal["text", "image", "file"] = "text"


class ChatSession(BaseModel):
    """A complete chat session."""
    session_id: str
    messages: list[ChatMessage]


class ChatQAReport(BaseModel):
    """Output report from chat compliance inspection."""
    session_id: str
    topics: list[str]
    compliance_score: float
    risk_level: RiskLevel
    violations: list[Violation]
    response_quality: float
    response_time_score: float


# --- TicketQA Models ---


class WorkOrder(BaseModel):
    """An after-sale work order."""
    order_id: str
    title: str
    description: str
    customer_messages: list[str]
    category_hint: str | None = None


class TicketQAReport(BaseModel):
    """Output report from work order intelligence."""
    order_id: str
    category: str
    risk_level: RiskLevel
    urgency: UrgencyLevel
    suggested_actions: list[str]
    key_issues: list[str]


# --- ViolationQA Models ---


class AgentInfo(BaseModel):
    """Information about the agent involved in a violation."""
    agent_id: str
    department: str | None = None
    role: str | None = None
    historical_violation_count: int = 0


class PunishmentSuggestion(BaseModel):
    """A suggested punishment for a violation."""
    type: str
    description: str
    score_deduction: float | None = None
    fine_amount: float | None = None


class PunishmentRule(BaseModel):
    """A rule mapping violation type to punishment escalation."""
    violation_type: str
    degree: ViolationDegree
    first_offense: str
    second_offense: str
    third_offense: str
    score_deduction: float


class ViolationInput(BaseModel):
    """Input to the violationqa module."""
    source_id: str
    source_type: Literal["call", "chat", "ticket"]
    violations: list[Violation]
    original_text: str
    agent_info: AgentInfo | None = None


class ViolationQAReport(BaseModel):
    """Output report from violation ticket processing."""
    violation_id: str
    source_id: str
    source_type: str
    summary: str
    degree: ViolationDegree
    punishment: PunishmentSuggestion
    audit_points: list[str]
    related_violations: list[str]
    is_repeat_offense: bool
