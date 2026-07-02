# langchain-riskqa-toolkit

> 🛡️ LangChain-based intelligent quality inspection toolkit for call QA, chat compliance, work order intelligence, and violation ticket processing.

## Features

- **callqa** — Phone call quality inspection: ASR transcript → rule + LLM compliance analysis → scoring report
- **chatqa** — Chat compliance inspection: IM messages → topic extraction + sensitive detection → compliance report
- **ticketqa** — Work order intelligence: ticket text → classification + risk assessment → suggested actions
- **violationqa** — Violation ticket processing: detected violations → ticket generation + severity grading + punishment suggestions

Each module is **independent and pluggable** — use one or chain them into a full QA → punishment pipeline.

## Quick Start

```bash
pip install riskqa-toolkit
```

```python
from riskqa.config import RiskQAConfig
from riskqa.callqa import CallQAChain, CallRuleEngine
from riskqa.core.schemas import CallTranscript, CallFragment

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = CallQAChain.from_config(config)

transcript = CallTranscript(
    call_id="demo-001",
    duration_seconds=60,
    fragments=[
        CallFragment(speaker="agent", start_time=0, end_time=30, text="您好，请问有什么可以帮您？"),
    ],
)

report = chain.invoke(transcript)
print(report.compliance_score, report.risk_level.value)
```

## Architecture

Each module follows the same pattern:

1. **RuleEngine** — Pure-Python keyword/regex matching (zero API calls)
2. **LLM Chains** — LangChain LCEL chains for semantic analysis
3. **ScoreAggregator** — Weighted fusion of rule + LLM scores
4. **Pydantic output** — Structured, type-safe reports

```
Input → RuleEngine → LLM Chains → ScoreAggregator → Report
```

## Configuration

```python
from riskqa.config import RiskQAConfig

# OpenAI
config = RiskQAConfig(llm_provider="openai", model_name="gpt-4o-mini")

# Ollama (local)
config = RiskQAConfig(llm_provider="ollama", model_name="llama3")

# Azure OpenAI
config = RiskQAConfig(llm_provider="azure", model_name="your-deployment")
```

Set `RISKQA_API_KEY` in your `.env` file.

## Pipeline: callqa → violationqa

```python
from riskqa.violationqa import ViolationQAChain, ViolationInput

call_report = call_chain.invoke(transcript)

if call_report.risk_level.value == "violation":
    violation_input = ViolationInput(
        source_id=call_report.call_id,
        source_type="call",
        violations=call_report.violations,
        original_text="...",
    )
    violation_report = violation_chain.invoke(violation_input)
```

## License

MIT
