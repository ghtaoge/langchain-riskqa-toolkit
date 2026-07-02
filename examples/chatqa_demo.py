"""Demo: Chat compliance inspection on a mock chat session."""

from riskqa.config import RiskQAConfig
from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import ChatSession
from riskqa.chatqa.chains import ChatQAChain

# Configure LLM (adjust provider/model as needed)
config = RiskQAConfig(
    model_name="gpt-4o-mini",
    # api_key is read from RISKQA_API_KEY env var
)

# Load mock chat session
session = DataAdapter.from_json_file("data/mock_chats/chat_demo_001.json", ChatSession)

# Run chat QA
chain = ChatQAChain.from_config(config)
report = chain.invoke(session)

# Print results
print(f"Session ID: {report.session_id}")
print(f"Topics: {report.topics}")
print(f"Compliance Score: {report.compliance_score}")
print(f"Risk Level: {report.risk_level.value}")
print(f"Violations: {len(report.violations)}")
for v in report.violations:
    print(f"  - {v.type}: {v.description} ({v.severity.value})")
print(f"Response Quality: {report.response_quality}")
print(f"Response Time Score: {report.response_time_score}")
