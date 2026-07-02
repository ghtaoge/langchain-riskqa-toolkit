"""Tests for the rule engine."""

from riskqa.core.schemas import Rule, SeverityLevel, RuleMatch
from riskqa.core.rule_engine import RuleEngine, default_rules


def test_single_keyword_rule():
    rules = [
        Rule(name="guarantee_keyword", pattern="保证", category="misleading_claim", severity=SeverityLevel.critical),
    ]
    engine = RuleEngine(rules)
    matches = engine.check("我保证这个产品一定有效")
    assert len(matches) == 1
    assert matches[0].rule_name == "guarantee_keyword"
    assert matches[0].matched_text == "保证"
    assert matches[0].severity == SeverityLevel.critical


def test_multiple_keyword_patterns():
    rules = [
        Rule(
            name="financial_keywords",
            pattern=["返利", "收益", "投资回报"],
            category="financial_promotion",
            severity=SeverityLevel.warning,
        ),
    ]
    engine = RuleEngine(rules)
    matches = engine.check("这个产品的投资回报率很高，还有返利")
    assert len(matches) == 2
    assert set(m.rule_name for m in matches) == {"financial_keywords"}


def test_regex_rule():
    rules = [
        Rule(
            name="phone_number_regex",
            pattern=r"\d{3}[*]{4}\d{4}",
            category="privacy_leak",
            severity=SeverityLevel.warning,
        ),
    ]
    engine = RuleEngine(rules)
    matches = engine.check("我的号码是138****1234")
    assert len(matches) == 1
    assert matches[0].matched_text == "138****1234"


def test_no_matches():
    rules = [
        Rule(name="test_rule", pattern="违规词", category="test", severity=SeverityLevel.info),
    ]
    engine = RuleEngine(rules)
    matches = engine.check("这是一段正常的话")
    assert len(matches) == 0


def test_empty_rules():
    engine = RuleEngine([])
    matches = engine.check("任意文本")
    assert len(matches) == 0


def test_position_tracking():
    rules = [
        Rule(name="pos_test", pattern="ABC", category="test", severity=SeverityLevel.info),
    ]
    engine = RuleEngine(rules)
    text = "xxxABCyyy"
    matches = engine.check(text)
    assert len(matches) == 1
    assert matches[0].position[0] == 3
    assert matches[0].position[1] == 6


def test_default_rules_exist():
    rules = default_rules()
    assert len(rules) > 0
    engine = RuleEngine(rules)
    # Should detect "保证" as a misleading claim
    matches = engine.check("我保证一定能治好")
    assert len(matches) >= 1
