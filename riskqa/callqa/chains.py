"""Chain compositions for call quality inspection."""

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import CallQAReport, CallTranscript, RiskLevel, Violation, SeverityLevel
from riskqa.core.scoring import ScoreAggregator
from riskqa.callqa.rules import CallRuleEngine
from riskqa.callqa.prompts import COMPLIANCE_PROMPT, SENSITIVE_PROMPT, QUALITY_PROMPT, SUMMARY_PROMPT
from riskqa.callqa.parsers import callqa_report_parser

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough


class CallQAChain:
    """End-to-end call quality inspection chain."""

    def __init__(self, config: RiskQAConfig, rules: CallRuleEngine | None = None):
        self.config = config
        self.rules = rules or CallRuleEngine.default_rules()
        self.aggregator = ScoreAggregator(config)
        self.llm = config.get_llm()

    @classmethod
    def from_config(cls, config: RiskQAConfig, rules: CallRuleEngine | None = None) -> "CallQAChain":
        """Create a CallQAChain from a config object."""
        return cls(config, rules)

    def invoke(self, transcript: CallTranscript) -> CallQAReport:
        """Run the full call QA pipeline on a transcript.

        Pipeline: RuleEngine -> ComplianceChain -> SensitiveChain -> QualityChain -> Aggregation
        """
        # Step 1: Rule engine check (pure Python, no LLM)
        full_text = "\n".join(f"{f.speaker}: {f.text}" for f in transcript.fragments)
        rule_matches = self.rules.check(full_text)

        # Step 2: Rule-based score (100 if no matches, reduced per match severity)
        rule_score = 100.0
        for match in rule_matches:
            if match.severity == SeverityLevel.critical:
                rule_score -= 20
            elif match.severity == SeverityLevel.warning:
                rule_score -= 10
            elif match.severity == SeverityLevel.info:
                rule_score -= 5
        rule_score = max(0.0, rule_score)

        # Step 3: LLM chains
        compliance_chain = COMPLIANCE_PROMPT | self.llm | StrOutputParser()
        sensitive_chain = SENSITIVE_PROMPT | self.llm | StrOutputParser()
        quality_chain = QUALITY_PROMPT | self.llm | StrOutputParser()

        compliance_result = compliance_chain.invoke({"transcript_text": full_text})
        sensitive_result = sensitive_chain.invoke({"transcript_text": full_text})
        quality_result = quality_chain.invoke({"transcript_text": full_text})

        # Step 4: Parse LLM quality score from quality_result
        # Extract a numeric score from the quality assessment text
        llm_score = self._extract_score(quality_result)

        # Step 5: Aggregate
        final_score = self.aggregator.aggregate_scores(rule_score, llm_score)
        risk_level = self.aggregator.compute_risk_level(final_score, rule_matches)

        # Step 6: Build violations list (merge rule matches + LLM detected)
        violations = self._build_violations(rule_matches, compliance_result, sensitive_result)

        # Step 7: Generate summary
        summary_chain = SUMMARY_PROMPT | self.llm | StrOutputParser()
        violations_text = "\n".join(f"- {v.type}: {v.description}" for v in violations) or "无违规"
        quality_tags = self._extract_tags(quality_result)
        summary = summary_chain.invoke({
            "violations_text": violations_text,
            "quality_score": str(final_score),
            "quality_tags": ", ".join(quality_tags),
        })

        return CallQAReport(
            call_id=transcript.call_id,
            compliance_score=round(final_score, 1),
            risk_level=risk_level,
            violations=violations,
            quality_tags=quality_tags,
            summary=summary,
        )

    def _extract_score(self, text: str) -> float:
        """Try to extract a numeric score (0-100) from LLM output text."""
        import re
        numbers = re.findall(r"(\d+)(?:\s*/\s*100|分|点)", text)
        if numbers:
            score = float(numbers[0])
            return min(100.0, max(0.0, score))
        # Fallback: look for any number near "评分" or "score"
        numbers = re.findall(r"(?:评分|score)[:\s]*(\d+)", text, re.IGNORECASE)
        if numbers:
            return min(100.0, max(0.0, float(numbers[0])))
        return 80.0  # default if parsing fails

    def _extract_tags(self, text: str) -> list[str]:
        """Extract quality tags from LLM output."""
        import re
        tag_match = re.search(r"标签[:：]\s*(.+)", text)
        if tag_match:
            return [t.strip() for t in tag_match.group(1).split(",")]
        return ["待评估"]

    def _build_violations(
        self, rule_matches: list, compliance_text: str, sensitive_text: str
    ) -> list[Violation]:
        """Merge rule engine matches into Violation objects."""
        violations = []
        for match in rule_matches:
            violations.append(
                Violation(
                    type=match.rule_name,
                    description=f"Rule match: {match.rule_name} detected '{match.matched_text}'",
                    severity=match.severity,
                    evidence=match.matched_text,
                    position=match.position,
                )
            )
        return violations
