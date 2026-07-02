# violationqa — 违规单处理模块

将检测到的违规信息转化为结构化的违规单，辅助严重度定级、处罚建议和审核要点。

这是质检流水线的下游模块：callqa/chatqa/ticketqa 检测出违规后，violationqa 将违规转化为可处理、可处罚的单据。

## 数据输入

```python
from riskqa.core.schemas import ViolationInput, Violation, AgentInfo, SeverityLevel

input = ViolationInput(
    source_id="call-001",
    source_type="call",  # call / chat / ticket
    violations=[
        Violation(type="misleading_claim", description="不当承诺", severity=SeverityLevel.critical, evidence="保证治好"),
    ],
    original_text="客服说：我保证治好你的病",
    agent_info=AgentInfo(agent_id="A001", historical_violation_count=1),  # 可选
)
```

## 运行违规单处理

```python
from riskqa.config import RiskQAConfig
from riskqa.violationqa import ViolationQAChain

config = RiskQAConfig(model_name="gpt-4o-mini")
chain = ViolationQAChain.from_config(config)
report = chain.invoke(input)
```

## 输出报告

```python
report.violation_id      # "VQ-abc123" (自动生成)
report.source_id         # "call-001"
report.source_type       # "call"
report.summary           # "客服在通话中做出不当医疗承诺..."
report.degree            # ViolationDegree.minor / moderate / severe / critical
report.punishment.type   # "书面警告" / "扣3分" / "罚款500元"
report.punishment.score_deduction  # 3.0
report.audit_points      # ["核实承诺内容", "确认通话记录"]
report.is_repeat_offense # True / False
```

## 处罚规则表

内置梯度处罚规则，根据违规类型和累犯次数自动匹配：

| 违规类型 | 首犯 | 累犯 | 三犯 | 扣分 |
|----------|------|------|------|------|
| misleading_claim | 书面警告 | 扣3分 | 罚款500元 | 3.0 |
| financial_promotion | 口头警告 | 扣1分 | 罚款200元 | 1.0 |
| privacy_violation | 扣5分 | 停职1天 | 解除合同 | 5.0 |
| unprofessional | 口头提醒 | 书面警告 | 扣1分 | 0.5 |

自定义处罚规则：

```python
from riskqa.violationqa import PunishmentRuleTable
from riskqa.core.schemas import PunishmentRule, ViolationDegree

custom_table = PunishmentRuleTable([
    PunishmentRule(violation_type="custom_type", degree=ViolationDegree.moderate,
                   first_offense="提醒", second_offense="扣2分", third_offense="罚款", score_deduction=2.0),
])
chain = ViolationQAChain(config, rule_table=custom_table)
```

## 与上游模块串联

```python
# callqa → violationqa 完整流水线
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

## 处理流程

```
违规检测结果 → SummarizeChain → SeverityChain(+规则引擎) → PunishmentChain(+处罚规则表) → AuditAssistChain → Report
```

特色：
- **双轨定级**：LLM 判断严重度 + 规则引擎约束（累犯加重、同类合并）
- **梯度处罚**：处罚规则表确保首犯/累犯/三犯有确定性梯度，LLM 在此基础上补充描述
- **审核辅助**：自动生成审核要点，加速人工审批流程
