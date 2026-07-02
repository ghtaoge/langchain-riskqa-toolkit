"""Tests for the callqa module."""

from riskqa.callqa.chains import CallQAChain
from riskqa.callqa.rules import CallRuleEngine
from riskqa.config import RiskQAConfig
from riskqa.core.schemas import CallFragment, CallTranscript, RiskLevel
from tests.conftest import make_fake_llm


def _make_transcript(text_agent: str, text_customer: str = "咨询") -> CallTranscript:
    return CallTranscript(
        call_id="test-001",
        duration_seconds=60,
        fragments=[
            CallFragment(speaker="agent", start_time=0, end_time=30, text=text_agent),
            CallFragment(speaker="customer", start_time=30, end_time=60, text=text_customer),
        ],
    )


def test_call_rule_engine_default_rules():
    engine = CallRuleEngine.default_rules()
    assert len(engine.rules) > 0


def test_call_rule_engine_detect_guarantee():
    engine = CallRuleEngine.default_rules()
    matches = engine.check("我保证治好你的病")
    assert len(matches) >= 1
    assert any(m.rule_name == "medical_guarantee" for m in matches)


def test_call_rule_engine_no_violation():
    engine = CallRuleEngine.default_rules()
    matches = engine.check("您好，请问有什么可以帮您？")
    assert len(matches) == 0


def test_callqa_chain_safe_call():
    """Test a clean call with mocked LLM returning high scores."""
    config = RiskQAConfig(model_name="gpt-4o-mini", api_key="test-key")
    chain = CallQAChain(config)

    # Pipeline invokes LLM 4 times: compliance, sensitive, quality, summary
    chain.llm = make_fake_llm([
        "无违规内容",
        "无敏感内容",
        "评分: 95分。标签: 专业, 礼貌。通话质量良好。",
        "通话质量良好，服务专业。",
    ])

    transcript = _make_transcript("您好，请问有什么可以帮您？")
    report = chain.invoke(transcript)

    assert report.call_id == "test-001"
    assert report.compliance_score > 0
    assert report.risk_level in [RiskLevel.safe, RiskLevel.warning, RiskLevel.violation]
    assert isinstance(report.summary, str)


def test_callqa_chain_violation_call():
    """Test a call with rule violations."""
    config = RiskQAConfig(model_name="gpt-4o-mini", api_key="test-key")
    chain = CallQAChain(config)

    chain.llm = make_fake_llm([
        "存在不当医疗承诺违规",
        "检测到绝对化用语",
        "评分: 40分。存在严重违规。标签: 违规, 不专业",
        "通话存在严重违规，包括不当承诺。",
    ])

    transcript = _make_transcript("我保证治好你的病，一定有效")
    report = chain.invoke(transcript)

    assert report.risk_level == RiskLevel.violation
    assert len(report.violations) >= 1
