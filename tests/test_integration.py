"""Integration tests verifying end-to-end pipelines with mock data."""

from pathlib import Path

from riskqa.config import RiskQAConfig
from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import CallTranscript, ChatSession, WorkOrder, ViolationInput, RiskLevel
from riskqa.callqa.chains import CallQAChain
from riskqa.chatqa.chains import ChatQAChain
from riskqa.ticketqa.chains import TicketQAChain
from riskqa.violationqa.chains import ViolationQAChain

from tests.conftest import make_fake_llm

DATA_DIR = Path(__file__).parent.parent / "data"


def test_load_mock_call_from_file():
    path = DATA_DIR / "mock_calls" / "call_demo_001.json"
    transcript = DataAdapter.from_json_file(path, CallTranscript)
    assert transcript.call_id == "call-demo-001"
    assert len(transcript.fragments) > 0


def test_load_mock_chat_from_file():
    path = DATA_DIR / "mock_chats" / "chat_demo_001.json"
    session = DataAdapter.from_json_file(path, ChatSession)
    assert session.session_id == "chat-demo-001"


def test_load_mock_ticket_from_file():
    path = DATA_DIR / "mock_tickets" / "ticket_demo_001.json"
    order = DataAdapter.from_json_file(path, WorkOrder)
    assert order.order_id == "WO-demo-001"


def test_load_mock_violation_from_file():
    path = DATA_DIR / "mock_violations" / "violation_demo_001.json"
    input = DataAdapter.from_json_file(path, ViolationInput)
    assert input.source_id == "call-demo-002"
    assert len(input.violations) >= 1


def test_callqa_violationqa_pipeline():
    """Full pipeline: callqa detects violation -> violationqa processes it."""
    config = RiskQAConfig(api_key="test-key")

    # Load violation call
    path = DATA_DIR / "mock_calls" / "call_demo_002_violation.json"
    transcript = DataAdapter.from_json_file(path, CallTranscript)

    # Run callqa with fake LLM
    # callqa pipeline: compliance, sensitive, quality, summary (4 LLM calls)
    call_chain = CallQAChain(config)
    call_chain.llm = make_fake_llm([
        "存在不当医疗承诺、金融收益承诺和隐私泄露违规",
        "检测到敏感内容：不当保证和索要隐私信息",
        "评分: 30分。标签: 违规, 不专业。存在严重违规。",
        "通话存在严重违规，包括不当承诺、金融诱导和索要隐私信息。",
    ])
    call_report = call_chain.invoke(transcript)

    assert call_report.risk_level == RiskLevel.violation
    assert len(call_report.violations) >= 1

    # If violation detected, run violationqa
    if call_report.risk_level == RiskLevel.violation:
        violation_chain = ViolationQAChain(config)
        # violationqa pipeline: summarize, severity, punishment, audit (4 LLM calls)
        violation_chain.llm = make_fake_llm([
            "客服在通话中做出不当医疗承诺、诱导金融投资并索要客户身份证号，多项严重违规。",
            "严重度：critical。多项严重违规叠加，涉及隐私泄露。",
            "处罚建议：扣5分，停职1天。",
            "1.核实通话录音中承诺内容\n2.确认身份证号索要行为\n3.检查金融诱导言论\n4.评估处罚合理性",
        ])
        violation_input = ViolationInput(
            source_id=call_report.call_id,
            source_type="call",
            violations=call_report.violations,
            original_text="客服在通话中做出不当保证",
        )
        violation_report = violation_chain.invoke(violation_input)

        assert violation_report.source_id == call_report.call_id
        assert violation_report.degree.value in ["severe", "critical"]
        assert violation_report.punishment is not None
