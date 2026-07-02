# langchain-riskqa-toolkit

> 🛡️ 基于 LangChain 的智能质检场景化工具集 — 通话质检、聊天合规、工单智能、违规单处理

## 功能模块

- **callqa** — 通话质检：ASR 转写文本 → 规则引擎 + LLM 合规分析 → 评分报告
- **chatqa** — 聊天合规：IM 消息流 → 话题抽取 + 敏感检测 → 合规报告
- **ticketqa** — 工单智能：工单文本 → 分类 + 风险定级 → 处理建议
- **violationqa** — 违规单处理：检测到的违规 → 单据生成 + 严重度定级 + 处罚建议

四个模块 **独立可插拔** — 可以单独使用任意一个，也可以串联成完整的 质检→处罚 流水线。

## 快速开始

### 安装

```bash
pip install riskqa-toolkit
```

### 通话质检示例

```python
from riskqa.config import RiskQAConfig
from riskqa.callqa import CallQAChain
from riskqa.core.schemas import CallTranscript, CallFragment

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = CallQAChain.from_config(config)

transcript = CallTranscript(
    call_id="demo-001",
    duration_seconds=60,
    fragments=[
        CallFragment(speaker="agent", start_time=0, end_time=30, text="您好，请问有什么可以帮您？"),
        CallFragment(speaker="customer", start_time=30, end_time=60, text="我想咨询产品A"),
    ],
)

report = chain.invoke(transcript)
print(f"合规评分: {report.compliance_score}")
print(f"风险等级: {report.risk_level.value}")
print(f"违规条目: {len(report.violations)}")
print(f"质量标签: {report.quality_tags}")
print(f"质检总结: {report.summary}")
```

### 聊天合规示例

```python
from riskqa.chatqa import ChatQAChain
from riskqa.core.schemas import ChatSession, ChatMessage
from datetime import datetime

session = ChatSession(
    session_id="demo-chat",
    messages=[
        ChatMessage(sender="agent", timestamp=datetime(2026, 1, 1, 10, 0), content="您好，请问有什么可以帮您？"),
        ChatMessage(sender="customer", timestamp=datetime(2026, 1, 1, 10, 1), content="我想咨询产品A"),
    ],
)

chain = ChatQAChain.from_config(config)
report = chain.invoke(session)
# report.topics → ["产品咨询"]
# report.compliance_score → 92.0
# report.response_quality → 88.0
```

### 工单智能示例

```python
from riskqa.ticketqa import TicketQAChain
from riskqa.core.schemas import WorkOrder

order = WorkOrder(
    order_id="WO-001",
    title="产品质量问题反馈",
    description="客户反馈产品使用异常",
    customer_messages=["产品使用一周后出现故障"],
)

chain = TicketQAChain.from_config(config)
report = chain.invoke(order)
# report.category → "售后"
# report.risk_level → RiskLevel.safe
# report.urgency → UrgencyLevel.medium
# report.suggested_actions → ["联系客户确认情况", "安排售后人员跟进"]
```

## 架构设计

每个模块遵循统一模式：

1. **规则引擎** — 纯 Python 关键词/正则匹配，零 API 调用，快速筛出明显违规
2. **LLM 链** — LangChain LCEL 链做语义深度分析（合规检测、敏感内容、质量评估）
3. **评分聚合** — 规则引擎结果 + LLM 结果加权融合（默认 0.4 + 0.6）
4. **Pydantic 输出** — 所有输出结构化、类型安全，避免 LLM 输出不可控

```
输入文本 → 规则引擎(关键词/正则) → LLM 链(语义分析) → 评分聚合 → 结构化报告
```

## 串流水线：质检 → 违规单

callqa/chatqa/ticketqa 检测违规后，可直接串联 violationqa 生成违规单：

```python
from riskqa.violationqa import ViolationQAChain, ViolationInput
from riskqa.core.schemas import AgentInfo

call_report = call_chain.invoke(transcript)

if call_report.risk_level.value == "violation":
    violation_input = ViolationInput(
        source_id=call_report.call_id,
        source_type="call",
        violations=call_report.violations,
        original_text="客服在通话中使用了不当承诺话术",
        agent_info=AgentInfo(agent_id="A001", historical_violation_count=1),
    )
    violation_chain = ViolationQAChain.from_config(config)
    violation_report = violation_chain.invoke(violation_input)

    # violation_report.degree → ViolationDegree.severe
    # violation_report.punishment.type → "扣3分"
    # violation_report.audit_points → ["核实承诺内容真实性", "确认通话记录"]
    # violation_report.is_repeat_offense → True
```

## LLM 配置

支持多种 LLM 后端：

```python
from riskqa.config import RiskQAConfig

# OpenAI
config = RiskQAConfig(llm_provider="openai", model_name="gpt-4o-mini")

# Ollama 本地模型
config = RiskQAConfig(llm_provider="ollama", model_name="llama3")

# Azure OpenAI
config = RiskQAConfig(llm_provider="azure", model_name="your-deployment")

# 自定义 API
config = RiskQAConfig(llm_provider="custom", api_base="http://your-api-endpoint")
```

在 `.env` 文件中设置 `RISKQA_API_KEY`。

## 违规单处罚规则表

violationqa 内置梯度处罚规则，首犯/累犯/三犯逐级加重：

| 违规类型 | 首犯 | 累犯 | 三犯 | 扣分 |
|----------|------|------|------|------|
| 不当承诺 (misleading_claim) | 书面警告 | 扣3分 | 罚款500元 | 3.0 |
| 金融收益 (financial_promotion) | 口头警告 | 扣1分 | 罚款200元 | 1.0 |
| 隐私泄露 (privacy_violation) | 扣5分 | 停职1天 | 解除合同 | 5.0 |
| 不专业用语 (unprofessional) | 口头提醒 | 书面警告 | 扣1分 | 0.5 |

支持自定义处罚规则：

```python
from riskqa.violationqa import PunishmentRuleTable
from riskqa.core.schemas import PunishmentRule, ViolationDegree

custom_table = PunishmentRuleTable([
    PunishmentRule(
        violation_type="custom_type",
        degree=ViolationDegree.moderate,
        first_offense="提醒",
        second_offense="扣2分",
        third_offense="罚款",
        score_deduction=2.0,
    ),
])
chain = ViolationQAChain(config, rule_table=custom_table)
```

## 从文件加载数据

所有输入类型均可从 JSON 文件加载：

```python
from riskqa.core.adapters import DataAdapter

transcript = DataAdapter.from_json_file("data/mock_calls/call_demo_001.json", CallTranscript)
session = DataAdapter.from_json_file("data/mock_chats/chat_demo_001.json", ChatSession)
order = DataAdapter.from_json_file("data/mock_tickets/ticket_demo_001.json", WorkOrder)
```

## 项目结构

```
langchain-riskqa-toolkit/
├── riskqa/                    # 主包
│   ├── config.py              # 全局配置
│   ├── core/                  # 共享基础设施
│   │   ├── schemas.py         # Pydantic 数据模型
│   │   ├── rule_engine.py     # 规则引擎
│   │   ├── scoring.py         # 评分聚合
│   │   ├── adapters.py        # 数据适配器
│   ├── callqa/                # 通话质检
│   ├── chatqa/                # 聊天合规
│   ├── ticketqa/              # 工单智能
│   ├── violationqa/           # 违规单处理
├── data/                      # 脱敏 mock 数据
├── examples/                  # 可运行 demo
├── tests/                     # 测试
├── docs/                      # 文档
```

## 开发

```bash
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码检查
ruff check riskqa/ tests/
```

## 脱敏规范

本项目严格遵循脱敏规范，不包含任何真实个人信息：

- 客户姓名 → `张先生`、`李女士` 等占位名
- 电话号码 → `138****1234` 等脱敏格式
- 产品名称 → `产品A`、`产品B` 等通用名
- 内部系统 → 不包含任何内部 URL、API 地址、系统名

详见 [CONTRIBUTING.md](.github/CONTRIBUTING.md)。

## 许可证

MIT
