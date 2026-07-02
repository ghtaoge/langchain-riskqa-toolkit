"""Prompt templates for chat compliance inspection chains."""

from langchain_core.prompts import ChatPromptTemplate

TOPIC_EXTRACT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个聊天话题分析专家。从客户与客服/销售的聊天记录中提取主要话题标签。"),
        ("human", "聊天记录如下：\n{chat_text}\n\n请提取3-5个话题标签（如 产品咨询、投诉、售后、价格 等）。只返回标签列表，逗号分隔。"),
    ]
)

SENSITIVE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个聊天内容合规检测专家。分析聊天中的敏感内容和违规行为，包括不当承诺、隐私泄露、诱导私下联系等。"),
        ("human", "聊天记录如下：\n{chat_text}\n\n请检测是否存在合规违规。对每个违规点，给出：类型、描述、严重程度(info/warning/critical)、原文证据。"),
    ]
)

RESPONSE_QUALITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个客服响应质量评估专家。评估客服/销售的响应质量，包括：响应是否及时、内容是否专业、是否有效帮助客户。"),
        ("system", "评分范围 0-100。"),
        ("human", "聊天记录如下：\n{chat_text}\n\n请评估响应质量，给出：评分(0-100)、质量标签列表、响应时效评分(0-100)。"),
    ]
)
