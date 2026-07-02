"""Tests for core schema validation."""

from datetime import datetime

import pytest

from riskqa.core.schemas import (
    AgentInfo,
    CallFragment,
    CallQAReport,
    CallTranscript,
    ChatMessage,
    ChatSession,
    PunishmentRule,
    RiskLevel,
    SeverityLevel,
    Violation,
    ViolationDegree,
    ViolationInput,
    WorkOrder,
)


def test_severity_level_values():
    assert SeverityLevel.info == "info"
    assert SeverityLevel.warning == "warning"
    assert SeverityLevel.critical == "critical"


def test_risk_level_values():
    assert RiskLevel.safe == "safe"
    assert RiskLevel.warning == "warning"
    assert RiskLevel.violation == "violation"


def test_violation_creation():
    v = Violation(
        type="misleading_claim",
        description="Agent made an unauthorized promise",
        severity=SeverityLevel.critical,
        evidence="I guarantee this will cure your condition",
        position=(120, 145),
    )
    assert v.type == "misleading_claim"
    assert v.severity == SeverityLevel.critical
    assert v.position == (120, 145)


def test_call_fragment_valid():
    f = CallFragment(speaker="agent", start_time=0.0, end_time=10.5, text="Hello")
    assert f.speaker == "agent"
    assert f.text == "Hello"


def test_call_fragment_invalid_speaker():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CallFragment(speaker="unknown", start_time=0.0, end_time=10.0, text="Hello")


def test_call_transcript():
    transcript = CallTranscript(
        call_id="call-001",
        duration_seconds=180,
        fragments=[
            CallFragment(speaker="agent", start_time=0, end_time=10, text="您好"),
            CallFragment(speaker="customer", start_time=10, end_time=20, text="我想咨询"),
        ],
    )
    assert transcript.call_id == "call-001"
    assert len(transcript.fragments) == 2


def test_chat_session():
    session = ChatSession(
        session_id="chat-001",
        messages=[
            ChatMessage(sender="agent", timestamp=datetime(2026, 1, 1, 10, 0), content="您好"),
            ChatMessage(sender="customer", timestamp=datetime(2026, 1, 1, 10, 1), content="咨询"),
        ],
    )
    assert session.session_id == "chat-001"
    assert len(session.messages) == 2


def test_work_order():
    order = WorkOrder(
        order_id="WO-001",
        title="产品质量问题",
        description="客户反馈产品存在质量问题",
        customer_messages=["产品使用后出现异常"],
        category_hint="售后",
    )
    assert order.order_id == "WO-001"
    assert order.category_hint == "售后"


def test_work_order_no_hint():
    order = WorkOrder(
        order_id="WO-002",
        title="退款申请",
        description="客户申请退款",
        customer_messages=["我要退款"],
    )
    assert order.category_hint is None


def test_violation_input():
    vi = ViolationInput(
        source_id="call-001",
        source_type="call",
        violations=[Violation(type="misleading", description="test", severity=SeverityLevel.warning, evidence="test")],
        original_text="Agent said something inappropriate",
        agent_info=AgentInfo(agent_id="A001", historical_violation_count=2),
    )
    assert vi.source_type == "call"
    assert vi.agent_info.historical_violation_count == 2


def test_violation_degree_values():
    assert ViolationDegree.minor == "minor"
    assert ViolationDegree.moderate == "moderate"
    assert ViolationDegree.severe == "severe"
    assert ViolationDegree.critical == "critical"


def test_punishment_rule():
    pr = PunishmentRule(
        violation_type="misleading_claim",
        degree=ViolationDegree.severe,
        first_offense="警告",
        second_offense="扣3分",
        third_offense="罚款500元",
        score_deduction=3.0,
    )
    assert pr.first_offense == "警告"
    assert pr.score_deduction == 3.0


def test_call_qa_report():
    report = CallQAReport(
        call_id="call-001",
        compliance_score=85.0,
        risk_level=RiskLevel.safe,
        violations=[],
        quality_tags=["专业", "礼貌"],
        summary="通话质量良好，无明显违规",
    )
    assert report.compliance_score == 85.0
    assert report.risk_level == RiskLevel.safe
