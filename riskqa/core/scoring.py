"""Score aggregation utilities — weighted fusion of rule engine and LLM scores."""

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import RiskLevel, RuleMatch, SeverityLevel


class ScoreAggregator:
    """Combine rule engine and LLM scores with configurable weights, then determine risk level."""

    def __init__(self, config: RiskQAConfig):
        self.rule_weight = config.rule_weight
        self.llm_weight = config.llm_weight

    def aggregate_scores(self, rule_score: float, llm_score: float) -> float:
        """Weighted average of rule engine score and LLM score."""
        return self.rule_weight * rule_score + self.llm_weight * llm_score

    def compute_risk_level(self, score: float, rule_matches: list[RuleMatch]) -> RiskLevel:
        """Determine overall risk level based on score and rule match severity.

        - score >= 90 and no critical matches -> safe
        - score >= 70 and no critical matches -> warning
        - score < 70 OR any critical match -> violation
        """
        has_critical = any(m.severity == SeverityLevel.critical for m in rule_matches)

        if has_critical:
            return RiskLevel.violation
        if score >= 90:
            return RiskLevel.safe
        if score >= 70:
            return RiskLevel.warning
        return RiskLevel.violation
