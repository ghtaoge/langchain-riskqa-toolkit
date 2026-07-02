"""Chat-specific compliance rules."""

from riskqa.core.schemas import Rule, SeverityLevel
from riskqa.core.rule_engine import RuleEngine


class ChatRuleEngine(RuleEngine):
    """Rule engine pre-loaded with chat compliance rules."""

    @staticmethod
    def default_rules() -> "ChatRuleEngine":
        rules = [
            Rule(name="misleading_claim", pattern="保证", category="misleading_claim", severity=SeverityLevel.critical),
            Rule(name="financial_promotion", pattern=["返利", "收益保证"], category="financial_promotion", severity=SeverityLevel.warning),
            Rule(name="privacy_request", pattern=["身份证号", "银行卡号", "密码"], category="privacy_violation", severity=SeverityLevel.critical),
            Rule(name="competitor_referral", pattern="不如去别家买", category="competitor_referral", severity=SeverityLevel.info),
            Rule(name="offline_contact", pattern=["加我微信", "私下联系"], category="offline_contact", severity=SeverityLevel.warning),
        ]
        return ChatRuleEngine(rules)
