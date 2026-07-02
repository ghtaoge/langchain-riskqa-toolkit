"""Chain compositions for work order intelligence."""

import re

from langchain_core.output_parsers import StrOutputParser

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import TicketQAReport, WorkOrder, RiskLevel, UrgencyLevel, SeverityLevel
from riskqa.core.scoring import ScoreAggregator
from riskqa.ticketqa.rules import TicketRuleEngine
from riskqa.ticketqa.prompts import CLASSIFY_PROMPT, RISK_ASSESS_PROMPT, SUGGEST_PROMPT


class TicketQAChain:
    """End-to-end work order intelligence chain."""

    def __init__(self, config: RiskQAConfig, rules: TicketRuleEngine | None = None):
        self.config = config
        self.rules = rules or TicketRuleEngine.default_rules()
        self.aggregator = ScoreAggregator(config)
        self.llm = config.get_llm()

    @classmethod
    def from_config(cls, config: RiskQAConfig) -> "TicketQAChain":
        return cls(config)

    def invoke(self, order: WorkOrder) -> TicketQAReport:
        """Run the full ticket QA pipeline."""
        full_text = f"{order.title}\n{order.description}\n" + "\n".join(order.customer_messages)

        # Step 1: Rule engine
        rule_matches = self.rules.check(full_text)

        # Step 2: LLM classify
        classify_chain = CLASSIFY_PROMPT | self.llm | StrOutputParser()
        category = classify_chain.invoke({
            "title": order.title,
            "description": order.description,
            "customer_messages": ", ".join(order.customer_messages),
        }).strip()

        # Step 3: LLM risk assessment
        risk_chain = RISK_ASSESS_PROMPT | self.llm | StrOutputParser()
        risk_result = risk_chain.invoke({
            "title": order.title,
            "description": order.description,
            "customer_messages": ", ".join(order.customer_messages),
            "category": category,
        })

        risk_level = self._extract_risk_level(risk_result, rule_matches)
        urgency = self._extract_urgency(risk_result, rule_matches)

        # Step 4: LLM suggest
        suggest_chain = SUGGEST_PROMPT | self.llm | StrOutputParser()
        suggest_result = suggest_chain.invoke({
            "title": order.title,
            "description": order.description,
            "risk_level": risk_level.value,
            "urgency": urgency.value,
        })

        suggested_actions = self._extract_list(suggest_result, "处理建议")
        key_issues = self._extract_list(suggest_result, "核心问题")

        return TicketQAReport(
            order_id=order.order_id,
            category=category,
            risk_level=risk_level,
            urgency=urgency,
            suggested_actions=suggested_actions,
            key_issues=key_issues,
        )

    def _extract_risk_level(self, text: str, rule_matches: list) -> RiskLevel:
        has_critical = any(m.severity == SeverityLevel.critical for m in rule_matches)
        if has_critical:
            return RiskLevel.violation
        for level in [RiskLevel.violation, RiskLevel.warning, RiskLevel.safe]:
            if level.value in text.lower():
                return level
        return RiskLevel.warning

    def _extract_urgency(self, text: str, rule_matches: list) -> UrgencyLevel:
        has_critical = any(m.severity == SeverityLevel.critical for m in rule_matches)
        if has_critical:
            return UrgencyLevel.urgent
        for level in [UrgencyLevel.urgent, UrgencyLevel.high, UrgencyLevel.medium, UrgencyLevel.low]:
            if level.value in text.lower():
                return level
        return UrgencyLevel.medium

    def _extract_list(self, text: str, section_name: str) -> list[str]:
        pattern = rf"{section_name}[:：]\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text)
        if match:
            items = [item.strip().lstrip("1234567890.-) ") for item in match.group(1).split(",")]
            return items if items else ["待评估"]
        return ["待评估"]
