"""Tests for the ticketqa module."""

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import WorkOrder, RiskLevel, UrgencyLevel
from riskqa.ticketqa.chains import TicketQAChain
from riskqa.ticketqa.rules import TicketRuleEngine

from tests.conftest import make_fake_llm


def test_ticket_rule_engine():
    engine = TicketRuleEngine.default_rules()
    matches = engine.check("我要投诉！这事我要找律师起诉！")
    assert len(matches) >= 2  # "投诉" + "律师"/"起诉"


def test_ticketqa_chain_normal_order():
    config = RiskQAConfig(api_key="test-key")
    chain = TicketQAChain(config)

    # Pipeline invokes LLM 3 times: classify, risk assess, suggest
    chain.llm = make_fake_llm([
        "咨询",
        "风险等级：safe。紧急程度：low。客户只是咨询产品使用方法。",
        "处理建议：1.回复客户使用说明 2.跟进确认问题解决。核心问题：产品使用疑问",
    ])

    order = WorkOrder(
        order_id="WO-001",
        title="产品使用咨询",
        description="客户询问产品使用方法",
        customer_messages=["产品怎么用？"],
    )
    report = chain.invoke(order)

    assert report.order_id == "WO-001"
    assert report.category is not None
    assert report.risk_level in [RiskLevel.safe, RiskLevel.warning, RiskLevel.violation]


def test_ticketqa_chain_urgent_order():
    config = RiskQAConfig(api_key="test-key")
    chain = TicketQAChain(config)

    chain.llm = make_fake_llm([
        "投诉",
        "风险等级：violation。紧急程度：urgent。客户威胁法律行动。",
        "处理建议：1.立即处理 2.法务介入。核心问题：法律风险",
    ])

    order = WorkOrder(
        order_id="WO-002",
        title="紧急投诉-要起诉",
        description="客户说要找律师起诉我们",
        customer_messages=["我要起诉你们！"],
    )
    report = chain.invoke(order)

    assert report.risk_level == RiskLevel.violation
    assert report.urgency == UrgencyLevel.urgent
