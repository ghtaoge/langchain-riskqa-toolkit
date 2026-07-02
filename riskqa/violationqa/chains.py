"""Chain compositions for violation ticket processing."""

import uuid

from langchain_core.output_parsers import StrOutputParser

from riskqa.config import RiskQAConfig
from riskqa.core.schemas import (
    PunishmentSuggestion,
    SeverityLevel,
    ViolationDegree,
    ViolationInput,
    ViolationQAReport,
)
from riskqa.violationqa.prompts import (
    AUDIT_ASSIST_PROMPT,
    PUNISHMENT_PROMPT,
    SEVERITY_PROMPT,
    SUMMARIZE_PROMPT,
)
from riskqa.violationqa.rules import PunishmentRuleTable


class ViolationQAChain:
    """End-to-end violation ticket processing chain."""

    def __init__(self, config: RiskQAConfig, rule_table: PunishmentRuleTable | None = None):
        self.config = config
        self.rule_table = rule_table or PunishmentRuleTable.default_table()
        self.llm = config.get_llm()

    @classmethod
    def from_config(cls, config: RiskQAConfig) -> "ViolationQAChain":
        return cls(config)

    def invoke(self, input: ViolationInput) -> ViolationQAReport:
        """Run the full violation ticket processing pipeline."""
        violations_text = "\n".join(f"- {v.type}: {v.description} ({v.severity.value})" for v in input.violations)
        offense_count = input.agent_info.historical_violation_count if input.agent_info else 0
        agent_role = input.agent_info.role if input.agent_info else "未知"
        is_repeat = offense_count > 0

        # Step 1: LLM summarize
        summarize_chain = SUMMARIZE_PROMPT | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({
            "violations_text": violations_text,
            "original_text": input.original_text[:500],  # truncate for token limit
            "source_type": input.source_type,
        })

        # Step 2: LLM severity + rule engine cross-check
        severity_chain = SEVERITY_PROMPT | self.llm | StrOutputParser()
        severity_result = severity_chain.invoke({
            "violations_text": violations_text,
            "summary": summary,
            "offense_count": str(offense_count),
            "agent_role": agent_role,
        })
        degree = self._determine_degree(severity_result, input.violations, is_repeat)

        # Step 3: LLM punishment + rule table cross-check
        primary_type = input.violations[0].type if input.violations else "unknown"
        _ = self.rule_table.get_punishment(primary_type, offense_count + 1)  # noqa: F841
        rules_text = self._format_rules()

        punishment_chain = PUNISHMENT_PROMPT | self.llm | StrOutputParser()
        punishment_result = punishment_chain.invoke({
            "degree": degree.value,
            "violation_types": ", ".join(v.type for v in input.violations),
            "is_repeat": str(is_repeat),
            "offense_count": str(offense_count),
            "punishment_rules_text": rules_text,
        })

        punishment = self._build_punishment(punishment_result, primary_type, offense_count + 1, degree)

        # Step 4: LLM audit assist
        audit_chain = AUDIT_ASSIST_PROMPT | self.llm | StrOutputParser()
        audit_result = audit_chain.invoke({
            "summary": summary,
            "degree": degree.value,
            "punishment_text": f"{punishment.type}: {punishment.description}",
        })
        audit_points = self._extract_audit_points(audit_result)

        return ViolationQAReport(
            violation_id=f"VQ-{uuid.uuid4().hex[:8]}",
            source_id=input.source_id,
            source_type=input.source_type,
            summary=summary,
            degree=degree,
            punishment=punishment,
            audit_points=audit_points,
            related_violations=[],
            is_repeat_offense=is_repeat,
        )

    def _determine_degree(self, text: str, violations: list, is_repeat: bool) -> ViolationDegree:
        """Determine degree from LLM output + rule engine logic."""
        # Rule: if any critical violation or repeat offense, at least severe
        has_critical = any(v.severity == SeverityLevel.critical for v in violations)
        if has_critical and is_repeat:
            return ViolationDegree.critical
        if has_critical:
            return ViolationDegree.severe

        # Try parsing from LLM text
        for degree in [ViolationDegree.critical, ViolationDegree.severe, ViolationDegree.moderate, ViolationDegree.minor]:
            if degree.value in text.lower():
                return degree

        # Repeat offense bumps one level
        if is_repeat:
            return ViolationDegree.moderate
        return ViolationDegree.minor

    def _build_punishment(self, text: str, violation_type: str, offense_count: int, degree: ViolationDegree) -> PunishmentSuggestion:
        """Build punishment suggestion from LLM + rule table."""
        rule = self.rule_table.lookup(violation_type)
        rule_based_type = self.rule_table.get_punishment(violation_type, offense_count)

        # Extract from LLM text
        score_deduction = rule.score_deduction if rule else None

        return PunishmentSuggestion(
            type=rule_based_type,
            description=text[:200],
            score_deduction=score_deduction,
            fine_amount=None,
        )

    def _format_rules(self) -> str:
        """Format punishment rules for LLM context."""
        lines = []
        for rule in self.rule_table.rules:
            lines.append(f"- {rule.violation_type}: 首犯→{rule.first_offense}, 累犯→{rule.second_offense}, 三犯→{rule.third_offense}")
        return "\n".join(lines)

    def _extract_audit_points(self, text: str) -> list[str]:
        """Extract audit points from LLM output."""
        points = [line.strip().lstrip("1234567890.-) ") for line in text.split("\n") if line.strip()]
        return points[:5] if points else ["核实违规内容真实性", "确认涉事人员身份", "评估处罚合理性"]
