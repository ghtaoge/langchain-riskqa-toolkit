# chatqa — 聊天合规模块

对 IM 聊天消息（企微、微信等）进行合规性检查，检测话题、敏感内容、响应质量。

## 数据输入

```python
from riskqa.core.schemas import ChatSession, ChatMessage
from datetime import datetime

session = ChatSession(
    session_id="chat-001",
    messages=[
        ChatMessage(sender="agent", timestamp=datetime(2026, 1, 15, 10, 0), content="您好"),
        ChatMessage(sender="customer", timestamp=datetime(2026, 1, 15, 10, 1), content="咨询产品A"),
    ],
)
```

从 JSON 文件加载：

```python
from riskqa.core.adapters import DataAdapter
session = DataAdapter.from_json_file("data/mock_chats/chat_demo_001.json", ChatSession)
```

## 运行合规检查

```python
from riskqa.config import RiskQAConfig
from riskqa.chatqa import ChatQAChain

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = ChatQAChain.from_config(config)
report = chain.invoke(session)
```

## 输出报告

```python
report.session_id         # "chat-001"
report.topics             # ["产品咨询"]
report.compliance_score   # 92.0
report.risk_level         # RiskLevel.safe
report.violations         # []
report.response_quality   # 88.0 (响应质量评分)
report.response_time_score # 85.0 (响应时效评分)
```

## 内置规则

| 规则名 | 类别 | 严重度 |
|--------|------|--------|
| misleading_claim | misleading_claim | critical |
| financial_promotion | financial_promotion | warning |
| privacy_request | privacy_violation | critical |
| competitor_referral | competitor_referral | info |
| offline_contact | offline_contact | warning |

## 处理流程

```
消息流 → RuleEngine → TopicExtractChain → SensitiveChain → ResponseQualityChain → ScoreAggregator → Report
```

特色：除了合规检测，还提取聊天话题标签和评估响应时效，适合客服质量监控场景。
