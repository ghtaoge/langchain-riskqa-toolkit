"""Prompt templates for work order intelligence chains."""

from langchain_core.prompts import ChatPromptTemplate

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个售后工单分类专家。根据工单标题和描述，将其归入以下类别之一：投诉、咨询、售后、纠纷、退款、其他。"),
        ("human", "工单标题：{title}\n工单描述：{description}\n客户诉求：{customer_messages}\n\n请给出分类结果（一个类别名称）。"),
    ]
)

RISK_ASSESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个工单风险评估专家。评估工单的风险等级和紧急程度。"),
        ("system", "风险等级：safe/warning/violation。紧急程度：low/medium/high/urgent。"),
        ("human", "工单标题：{title}\n工单描述：{description}\n客户诉求：{customer_messages}\n分类：{category}\n\n请评估风险等级和紧急程度，并说明原因。"),
    ]
)

SUGGEST_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个售后处理建议专家。根据工单信息和风险评估，给出2-3条处理建议和核心问题提炼。"),
        ("human", "工单标题：{title}\n描述：{description}\n风险等级：{risk_level}\n紧急程度：{urgency}\n\n请给出：1) 处理建议列表 2) 核心问题提炼"),
    ]
)
