"""Tests for the violationqa module."""

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import (
    AgentInfo,
    SeverityLevel,
    Violation,
    ViolationDegree,
    ViolationInput,
)
from riskqa.violationqa.chains import ViolationQAChain
from riskqa.violationqa.rules import PunishmentRuleTable
from tests.conftest import make_fake_llm


def test_punishment_rule_table_default():
    table = PunishmentRuleTable.default_table()
    assert len(table.rules) > 0


def test_punishment_rule_table_lookup():
    table = PunishmentRuleTable.default_table()
    rule = table.lookup("misleading_claim")
    assert rule is not None
    assert rule.first_offense == "书面警告"


def test_punishment_rule_table_escalation():
    table = PunishmentRuleTable.default_table()
    assert table.get_punishment("misleading_claim", 1) == "书面警告"
    assert table.get_punishment("misleading_claim", 2) == "扣3分"
    assert table.get_punishment("misleading_claim", 3) == "罚款500元"


def test_punishment_unknown_type():
    table = PunishmentRuleTable.default_table()
    assert table.get_punishment("unknown_type", 1) == "警告"


def test_violationqa_chain_basic():
    config = RiskQAConfig(api_key="test-key")
    chain = ViolationQAChain(config)

    # Pipeline invokes LLM 4 times: summarize, severity, punishment, audit
    chain.llm = make_fake_llm([
        "客服在通话中做出不当医疗承诺，存在严重违规行为。",
        "严重度：severe。客服做出绝对化医疗保证，属于严重违规。",
        "处罚建议：扣3分，书面警告。",
        "1.核实承诺内容是否属实\n2.检查通话录音记录\n3.确认涉事人员身份",
    ])

    input = ViolationInput(
        source_id="call-001",
        source_type="call",
        violations=[
            Violation(type="misleading_claim", description="不当医疗承诺", severity=SeverityLevel.critical, evidence="保证治好"),
        ],
        original_text="客服说：我保证治好你的病",
    )
    report = chain.invoke(input)

    assert report.source_id == "call-001"
    assert report.source_type == "call"
    assert report.degree in [ViolationDegree.severe, ViolationDegree.critical]
    assert report.punishment is not None
    assert len(report.audit_points) > 0


def test_violationqa_chain_repeat_offense():
    config = RiskQAConfig(api_key="test-key")
    chain = ViolationQAChain(config)

    chain.llm = make_fake_llm([
        "客服再次违规，属于累犯，需加重处罚。",
        "严重度：critical。累犯加重处罚。",
        "处罚建议：罚款500元，扣3分。",
        "1.核实累犯记录\n2.确认处罚升级合理",
    ])

    input = ViolationInput(
        source_id="call-002",
        source_type="call",
        violations=[
            Violation(type="misleading_claim", description="再次不当承诺", severity=SeverityLevel.critical, evidence="保证"),
        ],
        original_text="客服再次保证",
        agent_info=AgentInfo(agent_id="A001", historical_violation_count=2),
    )
    report = chain.invoke(input)

    assert report.is_repeat_offense is True
    assert report.degree == ViolationDegree.critical
