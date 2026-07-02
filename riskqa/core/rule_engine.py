"""Pure-Python rule engine for keyword and regex pattern matching."""

import re

from riskqa.core.schemas import Rule, RuleMatch, SeverityLevel


class RuleEngine:
    """Check text against a set of keyword/regex rules. Zero API calls."""

    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def check(self, text: str) -> list[RuleMatch]:
        """Execute all rules against the text and return matches."""
        matches: list[RuleMatch] = []
        for rule in self.rules:
            patterns = rule.pattern if isinstance(rule.pattern, list) else [rule.pattern]
            for pattern in patterns:
                # Try regex first, then plain keyword match
                try:
                    for m in re.finditer(pattern, text):
                        matches.append(
                            RuleMatch(
                                rule_name=rule.name,
                                matched_text=m.group(),
                                position=(m.start(), m.end()),
                                severity=rule.severity,
                            )
                        )
                except re.error:
                    # Pattern is not a valid regex — treat as plain keyword
                    idx = text.find(pattern)
                    while idx != -1:
                        matches.append(
                            RuleMatch(
                                rule_name=rule.name,
                                matched_text=pattern,
                                position=(idx, idx + len(pattern)),
                                severity=rule.severity,
                            )
                        )
                        idx = text.find(pattern, idx + 1)
        return matches


def default_rules() -> list[Rule]:
    """Return a built-in set of generic compliance rules for demonstration.

    These are intentionally broad and de-personalized — no proprietary lexicons.
    """
    return [
        # Misleading claims
        Rule(name="guarantee_word", pattern="保证", category="misleading_claim", severity=SeverityLevel.critical),
        Rule(name="cure_word", pattern="治愈", category="misleading_claim", severity=SeverityLevel.critical),
        Rule(name="guaranteed_effect", pattern="一定有效", category="misleading_claim", severity=SeverityLevel.critical),
        Rule(
            name="absolute_words",
            pattern=["绝对", "百分之百", "完全"],
            category="misleading_claim",
            severity=SeverityLevel.warning,
        ),
        # Financial promotion
        Rule(
            name="financial_words",
            pattern=["返利", "收益", "投资回报"],
            category="financial_promotion",
            severity=SeverityLevel.warning,
        ),
        # Privacy / personal info
        Rule(
            name="privacy_patterns",
            pattern=[r"\d{11}", r"\d{3}[*]{4}\d{4}"],
            category="privacy_leak",
            severity=SeverityLevel.warning,
        ),
        # Competitor references
        Rule(name="competitor_switch", pattern="不如去买", category="competitor_referral", severity=SeverityLevel.info),
    ]
