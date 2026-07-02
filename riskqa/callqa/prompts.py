"""Prompt templates for call quality inspection chains."""

from langchain_core.prompts import ChatPromptTemplate

COMPLIANCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个通话质检专家。分析客服/销售人员的通话内容，判断是否存在合规违规。"),
        ("system", "判断标准：1) 是否做出不当承诺或保证 2) 是否涉及金融收益承诺 3) 是否泄露客户隐私 4) 是否使用绝对化用语"),
        ("human", "通话内容如下：\n{transcript_text}\n\n请逐条分析是否存在合规违规。对每个违规点，给出：违规类型、描述、严重程度(info/warning/critical)、原文证据。"),
    ]
)

SENSITIVE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个敏感内容检测专家。从语义层面分析通话中是否存在敏感或违规内容，不仅仅匹配关键词，而是理解上下文含义。"),
        ("human", "通话内容如下：\n{transcript_text}\n\n请识别任何在上下文中有敏感含义的内容，即使没有直接使用敏感关键词。对每个检测到的内容，给出：类型、描述、严重程度、原文证据。"),
    ]
)

QUALITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个通话服务质量评估专家。评估通话的服务质量，包括：态度是否专业、信息是否完整、是否有效解决客户问题。"),
        ("system", "评分范围 0-100，其中 90+ 为优质，70-89 为良好，60-69 为待改进，低于60为不合格。"),
        ("human", "通话内容如下：\n{transcript_text}\n\n请评估服务质量，给出：评分(0-100)、质量标签列表(如 专业/礼貌/完整 等)、一段话总结。"),
    ]
)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个通话质检报告生成专家。根据已有的违规信息和质量评估，生成一份简洁的质检总结。"),
        ("human", "违规信息：{violations_text}\n质量评分：{quality_score}\n质量标签：{quality_tags}\n\n请用一段话(不超过100字)总结这次通话的质检结果。"),
    ]
)
