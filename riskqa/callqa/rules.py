"""Call-specific compliance rules."""

from riskqa.core.rule_engine import RuleEngine
from riskqa.core.schemas import Rule, SeverityLevel


class CallRuleEngine(RuleEngine):
    """Rule engine pre-loaded with call-specific compliance rules."""

    @staticmethod
    def default_rules() -> "CallRuleEngine":
        """Return a CallRuleEngine with built-in call QA rules."""
        rules = [
            # Misleading medical claims
            Rule(name="medical_guarantee", pattern="保证治好", category="misleading_claim", severity=SeverityLevel.critical),
            Rule(name="guarantee_effect", pattern="一定有效", category="misleading_claim", severity=SeverityLevel.critical),
            Rule(name="absolute_words", pattern=["绝对有效", "百分之百", "完全治愈"], category="misleading_claim", severity=SeverityLevel.warning),
            # Required phrases (absence = violation — handled by LLM, not keyword)
            # Unauthorized financial promises
            Rule(name="financial_return", pattern=["返利", "投资回报率"], category="financial_promotion", severity=SeverityLevel.warning),
            # Privacy concerns
            Rule(name="personal_info_request", pattern=["身份证号", "银行卡号"], category="privacy_violation", severity=SeverityLevel.critical),
            # Unprofessional language
            Rule(name="informal_greeting", pattern="喂喂喂", category="unprofessional", severity=SeverityLevel.info),
        ]
        return CallRuleEngine(rules)
