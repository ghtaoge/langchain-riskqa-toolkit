"""Demo: Call quality inspection on a mock transcript."""

from riskqa.config import RiskQAConfig
from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import CallTranscript
from riskqa.callqa.chains import CallQAChain
from riskqa.callqa.rules import CallRuleEngine

# Configure LLM (adjust provider/model as needed)
config = RiskQAConfig(
    model_name="gpt-4o-mini",
    # api_key is read from RISKQA_API_KEY env var
)

# Load mock transcript
transcript = DataAdapter.from_json_file("data/mock_calls/call_demo_001.json", CallTranscript)

# Run call QA
chain = CallQAChain.from_config(config)
report = chain.invoke(transcript)

# Print results
print(f"Call ID: {report.call_id}")
print(f"Compliance Score: {report.compliance_score}")
print(f"Risk Level: {report.risk_level.value}")
print(f"Violations: {len(report.violations)}")
for v in report.violations:
    print(f"  - {v.type}: {v.description} ({v.severity.value})")
print(f"Quality Tags: {report.quality_tags}")
print(f"Summary: {report.summary}")
