"""Tests for the chatqa module."""

from datetime import datetime

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import ChatMessage, ChatSession, RiskLevel
from riskqa.chatqa.chains import ChatQAChain
from riskqa.chatqa.rules import ChatRuleEngine

from tests.conftest import make_fake_llm


def _make_session(messages: list[tuple[str, str]]) -> ChatSession:
    return ChatSession(
        session_id="chat-test-001",
        messages=[
            ChatMessage(sender=s, timestamp=datetime(2026, 1, 1, 10, i), content=c)
            for i, (s, c) in enumerate(messages)
        ],
    )


def test_chat_rule_engine_default():
    engine = ChatRuleEngine.default_rules()
    assert len(engine.rules) > 0


def test_chat_rule_engine_detect():
    engine = ChatRuleEngine.default_rules()
    matches = engine.check("我保证这个产品一定好，加我微信私下聊")
    assert len(matches) >= 2  # "保证" + "加我微信"


def test_chatqa_chain_safe_chat():
    config = RiskQAConfig(api_key="test-key")
    chain = ChatQAChain(config)

    # Pipeline invokes LLM 3 times: topic, sensitive, quality
    chain.llm = make_fake_llm([
        "产品咨询, 产品介绍",
        "无违规内容",
        "评分:92分。标签:专业,及时。响应时效:88",
    ])

    session = _make_session([
        ("agent", "您好，请问有什么可以帮您？"),
        ("customer", "我想了解一下产品A"),
        ("agent", "产品A是我们的主打产品，有什么具体问题吗？"),
    ])
    report = chain.invoke(session)

    assert report.session_id == "chat-test-001"
    assert report.compliance_score > 0
    assert len(report.topics) > 0


def test_chatqa_chain_violation_chat():
    config = RiskQAConfig(api_key="test-key")
    chain = ChatQAChain(config)

    chain.llm = make_fake_llm([
        "产品咨询, 违规承诺",
        "存在违规承诺和诱导私下联系",
        "评分:45分。存在违规。响应时效:60",
    ])

    session = _make_session([
        ("agent", "我保证产品一定有效，加我微信私下联系"),
    ])
    report = chain.invoke(session)

    assert report.risk_level == RiskLevel.violation
    assert len(report.violations) >= 1
