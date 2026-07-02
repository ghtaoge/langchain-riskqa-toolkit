"""Ticket-specific classification and urgency rules."""

from riskqa.core.schemas import Rule, SeverityLevel
from riskqa.core.rule_engine import RuleEngine


class TicketRuleEngine(RuleEngine):
    """Rule engine for work order classification hints."""

    @staticmethod
    def default_rules() -> "TicketRuleEngine":
        rules = [
            Rule(name="urgent_keyword", pattern=["紧急", "立刻", "马上"], category="urgency_hint", severity=SeverityLevel.critical),
            Rule(name="complaint_keyword", pattern=["投诉", "不满意", "差评"], category="complaint", severity=SeverityLevel.warning),
            Rule(name="legal_keyword", pattern=["律师", "法律", "起诉"], category="legal_risk", severity=SeverityLevel.critical),
            Rule(name="refund_keyword", pattern=["退款", "退货", "赔偿"], category="refund", severity=SeverityLevel.info),
        ]
        return TicketRuleEngine(rules)
