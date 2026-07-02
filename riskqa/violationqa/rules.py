"""Violation-specific rules including punishment rule table."""

from riskqa.core.schemas import PunishmentRule, ViolationDegree, SeverityLevel


class PunishmentRuleTable:
    """Lookup table for escalation-based punishment rules."""

    def __init__(self, rules: list[PunishmentRule]):
        self.rules = rules
        self._index = {r.violation_type: r for r in rules}

    def lookup(self, violation_type: str) -> PunishmentRule | None:
        return self._index.get(violation_type)

    def get_punishment(self, violation_type: str, offense_count: int) -> str:
        """Return punishment text based on violation type and offense count."""
        rule = self.lookup(violation_type)
        if rule is None:
            return "警告"  # default for unknown types
        if offense_count >= 3:
            return rule.third_offense
        if offense_count == 2:
            return rule.second_offense
        return rule.first_offense

    @staticmethod
    def default_table() -> "PunishmentRuleTable":
        """Return a built-in punishment rule table."""
        rules = [
            PunishmentRule(violation_type="misleading_claim", degree=ViolationDegree.severe, first_offense="书面警告", second_offense="扣3分", third_offense="罚款500元", score_deduction=3.0),
            PunishmentRule(violation_type="financial_promotion", degree=ViolationDegree.moderate, first_offense="口头警告", second_offense="扣1分", third_offense="罚款200元", score_deduction=1.0),
            PunishmentRule(violation_type="privacy_violation", degree=ViolationDegree.critical, first_offense="扣5分", second_offense="停职1天", third_offense="解除合同", score_deduction=5.0),
            PunishmentRule(violation_type="unprofessional", degree=ViolationDegree.minor, first_offense="口头提醒", second_offense="书面警告", third_offense="扣1分", score_deduction=0.5),
        ]
        return PunishmentRuleTable(rules)
