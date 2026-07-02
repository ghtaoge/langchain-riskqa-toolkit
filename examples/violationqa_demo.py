"""Demo: Violation ticket processing — pipeline from callqa to violationqa."""

from riskqa.config import RiskQAConfig
from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import CallTranscript, ViolationInput
from riskqa.callqa.chains import CallQAChain
from riskqa.violationqa.chains import ViolationQAChain

config = RiskQAConfig(model_name="gpt-4o-mini")

# Step 1: Call QA — detect violations
transcript = DataAdapter.from_json_file("data/mock_calls/call_demo_002_violation.json", CallTranscript)
call_chain = CallQAChain.from_config(config)
call_report = call_chain.invoke(transcript)

print(f"=== Call QA Report ===")
print(f"Risk Level: {call_report.risk_level.value}")
print(f"Violations: {len(call_report.violations)}")

# Step 2: If violations detected, generate violation ticket
if call_report.risk_level.value == "violation":
    violation_input = ViolationInput(
        source_id=call_report.call_id,
        source_type="call",
        violations=call_report.violations,
        original_text="客服在通话中做出不当保证并索要隐私信息",
    )
    violation_chain = ViolationQAChain.from_config(config)
    violation_report = violation_chain.invoke(violation_input)

    print(f"\n=== Violation Ticket Report ===")
    print(f"Violation ID: {violation_report.violation_id}")
    print(f"Degree: {violation_report.degree.value}")
    print(f"Summary: {violation_report.summary}")
    print(f"Punishment: {violation_report.punishment.type}")
    print(f"Audit Points: {violation_report.audit_points}")
else:
    print("No violations detected — no violation ticket needed.")
