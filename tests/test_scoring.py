"""Tests for score aggregation utilities."""

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import RiskLevel, RuleMatch, SeverityLevel
from riskqa.core.scoring import ScoreAggregator


def test_aggregate_rule_and_llm_scores():
    config = RiskQAConfig(rule_weight=0.4, llm_weight=0.6)
    aggregator = ScoreAggregator(config)
    # rule_score=60 (has violations), llm_score=90 (minor issues)
    final = aggregator.aggregate_scores(rule_score=60.0, llm_score=90.0)
    assert final == 0.4 * 60.0 + 0.6 * 90.0  # = 78.0


def test_compute_risk_level_safe():
    aggregator = ScoreAggregator(RiskQAConfig())
    level = aggregator.compute_risk_level(95.0, rule_matches=[])
    assert level == RiskLevel.safe


def test_compute_risk_level_warning():
    aggregator = ScoreAggregator(RiskQAConfig())
    level = aggregator.compute_risk_level(75.0, rule_matches=[])
    assert level == RiskLevel.warning


def test_compute_risk_level_violation():
    aggregator = ScoreAggregator(RiskQAConfig())
    matches = [RuleMatch(rule_name="test", matched_text="test", position=(0, 1), severity=SeverityLevel.critical)]
    level = aggregator.compute_risk_level(50.0, rule_matches=matches)
    assert level == RiskLevel.violation


def test_violation_with_high_score():
    aggregator = ScoreAggregator(RiskQAConfig())
    # Even if score is decent, critical rule match overrides to violation
    matches = [RuleMatch(rule_name="test", matched_text="test", position=(0, 1), severity=SeverityLevel.critical)]
    level = aggregator.compute_risk_level(85.0, rule_matches=matches)
    assert level == RiskLevel.violation


def test_zero_scores():
    aggregator = ScoreAggregator(RiskQAConfig())
    final = aggregator.aggregate_scores(rule_score=0.0, llm_score=0.0)
    assert final == 0.0


def test_perfect_scores():
    aggregator = ScoreAggregator(RiskQAConfig())
    final = aggregator.aggregate_scores(rule_score=100.0, llm_score=100.0)
    assert final == 100.0
