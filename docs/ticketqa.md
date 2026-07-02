# ticketqa — 工单智能模块

对售后工单进行智能分类、风险定级、紧急度评估，并生成处理建议。

## 数据输入

```python
from riskqa.core.schemas import WorkOrder

order = WorkOrder(
    order_id="WO-001",
    title="产品质量问题反馈",
    description="客户反馈产品出现异常",
    customer_messages=["产品使用一周后出现故障"],
    category_hint="售后",  # 可选分类提示
)
```

从 JSON 文件加载：

```python
from riskqa.core.adapters import DataAdapter
order = DataAdapter.from_json_file("data/mock_tickets/ticket_demo_001.json", WorkOrder)
```

## 运行工单分析

```python
from riskqa.config import RiskQAConfig
from riskqa.ticketqa import TicketQAChain

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = TicketQAChain.from_config(config)
report = chain.invoke(order)
```

## 输出报告

```python
report.order_id          # "WO-001"
report.category          # "售后" / "投诉" / "咨询" / "纠纷" / "退款"
report.risk_level        # RiskLevel.safe / warning / violation
report.urgency           # UrgencyLevel.low / medium / high / urgent
report.suggested_actions # ["联系客户", "安排售后人员"]
report.key_issues        # ["产品质量异常"]
```

## 内置规则

| 规则名 | 类别 | 严重度 |
|--------|------|--------|
| urgent_keyword | urgency_hint | critical |
| complaint_keyword | complaint | warning |
| legal_keyword | legal_risk | critical |
| refund_keyword | refund | info |

## 处理流程

```
工单文本 → RuleEngine → ClassifyChain → RiskAssessChain → SuggestChain → Report
```

特色：三步链式分析 — 先分类，再根据分类做风险评估，最后根据风险生成建议。每一步的结果都传递给下一步，形成递进式推理。
