# Quick Start Guide

## Installation

```bash
pip install riskqa-toolkit
```

For Ollama support:
```bash
pip install riskqa-toolkit[ollama]
```

## Setting up your LLM

Create a `.env` file:
```
RISKQA_API_KEY=your-openai-api-key
```

Or configure in code:
```python
from riskqa.config import RiskQAConfig

config = RiskQAConfig(
    llm_provider="openai",
    model_name="gpt-4o-mini",
    api_key="your-key",
)
```

## Running your first inspection

### Call QA

```python
from riskqa.callqa import CallQAChain
from riskqa.core.schemas import CallTranscript, CallFragment

chain = CallQAChain.from_config(RiskQAConfig())
transcript = CallTranscript(
    call_id="test", duration_seconds=60,
    fragments=[CallFragment(speaker="agent", start_time=0, end_time=30, text="您好")],
)
report = chain.invoke(transcript)
```

### Chat Compliance

```python
from riskqa.chatqa import ChatQAChain
from riskqa.core.schemas import ChatSession, ChatMessage

chain = ChatQAChain.from_config(RiskQAConfig())
session = ChatSession(session_id="test", messages=[...])
report = chain.invoke(session)
```

### Work Order Intelligence

```python
from riskqa.ticketqa import TicketQAChain
from riskqa.core.schemas import WorkOrder

chain = TicketQAChain.from_config(RiskQAConfig())
order = WorkOrder(order_id="test", title="咨询", description="...", customer_messages=[...])
report = chain.invoke(order)
```

### Violation Ticket Processing

```python
from riskqa.violationqa import ViolationQAChain
from riskqa.core.schemas import ViolationInput

chain = ViolationQAChain.from_config(RiskQAConfig())
input = ViolationInput(source_id="call-001", source_type="call", violations=[...], original_text="...")
report = chain.invoke(input)
```
