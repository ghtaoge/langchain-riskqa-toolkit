"""Demo: Work order intelligence on a mock ticket."""

from riskqa.config import RiskQAConfig
from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import WorkOrder
from riskqa.ticketqa.chains import TicketQAChain

# Configure LLM (adjust provider/model as needed)
config = RiskQAConfig(
    model_name="gpt-4o-mini",
    # api_key is read from RISKQA_API_KEY env var
)

# Load mock work order
order = DataAdapter.from_json_file("data/mock_tickets/ticket_demo_001.json", WorkOrder)

# Run ticket QA
chain = TicketQAChain.from_config(config)
report = chain.invoke(order)

# Print results
print(f"Order ID: {report.order_id}")
print(f"Category: {report.category}")
print(f"Risk Level: {report.risk_level.value}")
print(f"Urgency: {report.urgency.value}")
print(f"Suggested Actions: {report.suggested_actions}")
print(f"Key Issues: {report.key_issues}")
