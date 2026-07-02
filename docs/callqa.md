# callqa — 通话质检模块

对 ASR 转写的通话内容进行合规性检查，检测不当承诺、敏感内容、服务质量问题。

## 数据输入

```python
from riskqa.core.schemas import CallTranscript, CallFragment

transcript = CallTranscript(
    call_id="demo-001",
    duration_seconds=180,
    fragments=[
        CallFragment(speaker="agent", start_time=0, end_time=30, text="您好，请问有什么可以帮您？"),
        CallFragment(speaker="customer", start_time=30, end_time=60, text="我想咨询产品A"),
    ],
)
```

也可以从 JSON 文件加载：

```python
from riskqa.core.adapters import DataAdapter
transcript = DataAdapter.from_json_file("data/mock_calls/call_demo_001.json", CallTranscript)
```

## 运行质检

```python
from riskqa.config import RiskQAConfig
from riskqa.callqa import CallQAChain

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = CallQAChain.from_config(config)
report = chain.invoke(transcript)
```

## 输出报告

```python
report.call_id           # "demo-001"
report.compliance_score  # 85.0 (0-100)
report.risk_level        # RiskLevel.safe / warning / violation
report.violations        # list[Violation]
report.quality_tags      # ["专业", "礼貌"]
report.summary           # "通话质量良好，无明显违规"
```

## 内置规则

默认规则引擎检测以下类别：

| 规则名 | 类别 | 严重度 |
|--------|------|--------|
| medical_guarantee | misleading_claim | critical |
| guarantee_effect | misleading_claim | critical |
| absolute_words | misleading_claim | warning |
| financial_words | financial_promotion | warning |
| personal_info_request | privacy_violation | critical |
| informal_greeting | unprofessional | info |

自定义规则：

```python
from riskqa.callqa.rules import CallRuleEngine
from riskqa.core.schemas import Rule, SeverityLevel

custom_rules = CallRuleEngine([
    Rule(name="my_rule", pattern="我的关键词", category="custom", severity=SeverityLevel.warning),
])
chain = CallQAChain.from_config(config, rules=custom_rules)
```

## 处理流程

```
原始转写 → RuleEngine(关键词/正则) → ComplianceChain(LLM合规) → SensitiveChain(LLM敏感) → QualityChain(LLM质量) → ScoreAggregator → Report
```

- RuleEngine 纯 Python，零 API 调用，快速筛出明显违规
- LLM Chain 对规则标记可疑或全量文本做语义深度分析
- 最终分数 = rule_weight × 规则分 + llm_weight × LLM 分（默认 0.4 + 0.6）
