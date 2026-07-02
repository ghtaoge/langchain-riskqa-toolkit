"""Chain compositions for chat compliance inspection."""

import re

from langchain_core.output_parsers import StrOutputParser

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import ChatQAReport, ChatSession, RiskLevel, Violation, SeverityLevel
from riskqa.core.scoring import ScoreAggregator
from riskqa.chatqa.rules import ChatRuleEngine
from riskqa.chatqa.prompts import TOPIC_EXTRACT_PROMPT, SENSITIVE_PROMPT, RESPONSE_QUALITY_PROMPT


class ChatQAChain:
    """End-to-end chat compliance inspection chain."""

    def __init__(self, config: RiskQAConfig, rules: ChatRuleEngine | None = None):
        self.config = config
        self.rules = rules or ChatRuleEngine.default_rules()
        self.aggregator = ScoreAggregator(config)
        self.llm = config.get_llm()

    @classmethod
    def from_config(cls, config: RiskQAConfig, rules: ChatRuleEngine | None = None) -> "ChatQAChain":
        return cls(config, rules)

    def invoke(self, session: ChatSession) -> ChatQAReport:
        """Run the full chat QA pipeline."""
        # Format chat text
        chat_text = "\n".join(
            f"[{m.timestamp.strftime('%H:%M')}] {m.sender}: {m.content}" for m in session.messages
        )

        # Step 1: Rule engine
        rule_matches = self.rules.check(chat_text)
        rule_score = 100.0
        for match in rule_matches:
            if match.severity == SeverityLevel.critical:
                rule_score -= 20
            elif match.severity == SeverityLevel.warning:
                rule_score -= 10
            else:
                rule_score -= 5
        rule_score = max(0.0, rule_score)

        # Step 2: LLM chains
        topic_chain = TOPIC_EXTRACT_PROMPT | self.llm | StrOutputParser()
        sensitive_chain = SENSITIVE_PROMPT | self.llm | StrOutputParser()
        quality_chain = RESPONSE_QUALITY_PROMPT | self.llm | StrOutputParser()

        topics_result = topic_chain.invoke({"chat_text": chat_text})
        sensitive_result = sensitive_chain.invoke({"chat_text": chat_text})
        quality_result = quality_chain.invoke({"chat_text": chat_text})

        # Step 3: Parse results
        topics = [t.strip() for t in topics_result.split(",")] if topics_result else ["未识别"]
        llm_score = self._extract_score(quality_result)
        response_quality = self._extract_score(quality_result)
        response_time_score = self._extract_response_time_score(quality_result)

        # Step 4: Aggregate
        final_score = self.aggregator.aggregate_scores(rule_score, llm_score)
        risk_level = self.aggregator.compute_risk_level(final_score, rule_matches)

        # Step 5: Build violations
        violations = [
            Violation(
                type=m.rule_name,
                description=f"Rule match: {m.rule_name} detected '{m.matched_text}'",
                severity=m.severity,
                evidence=m.matched_text,
                position=m.position,
            )
            for m in rule_matches
        ]

        return ChatQAReport(
            session_id=session.session_id,
            topics=topics[:5],
            compliance_score=round(final_score, 1),
            risk_level=risk_level,
            violations=violations,
            response_quality=round(response_quality, 1),
            response_time_score=round(response_time_score, 1),
        )

    def _extract_score(self, text: str) -> float:
        numbers = re.findall(r"(\d+)(?:\s*/\s*100|分)", text)
        if numbers:
            return min(100.0, max(0.0, float(numbers[0])))
        return 80.0

    def _extract_response_time_score(self, text: str) -> float:
        match = re.search(r"响应时效[:\s]*(\d+)", text)
        if match:
            return min(100.0, max(0.0, float(match.group(1))))
        return 75.0
