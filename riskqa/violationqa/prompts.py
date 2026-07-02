"""Prompt templates for violation ticket processing chains."""

from langchain_core.prompts import ChatPromptTemplate

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个违规单描述生成专家。根据检测到的违规条目和原始文本，提炼违规要点，编写一段结构化的违规单摘要。"),
        ("human", "违规条目：\n{violations_text}\n原始文本：\n{original_text}\n来源类型：{source_type}\n\n请生成违规单摘要(不超过150字)，包含：违规类型、核心事实、涉及人员角色。"),
    ]
)

SEVERITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个违规严重度定级专家。根据违规类型、上下文和涉事人员历史记录，判定严重度等级。"),
        ("system", "等级：minor(轻微) / moderate(一般) / severe(严重) / critical(极严重)"),
        ("human", "违规条目：\n{violations_text}\n原始文本摘要：{summary}\n涉事人员历史违规次数：{offense_count}\n涉事人员角色：{agent_role}\n\n请判定严重度等级并说明理由。"),
    ]
)

PUNISHMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个处罚建议生成专家。根据严重度等级和违规历史，给出合理的处罚建议。"),
        ("system", "参考处罚规则：{punishment_rules_text}"),
        ("human", "严重度：{degree}\n违规类型：{violation_types}\n是否累犯：{is_repeat}\n历史违规次数：{offense_count}\n\n请给出处罚建议，包括：处罚类型、描述、扣分值(如有)。"),
    ]
)

AUDIT_ASSIST_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个审核辅助专家。为审核人员生成3-5条审核要点，帮助他们快速判断违规单是否合理。"),
        ("human", "违规摘要：{summary}\n严重度：{degree}\n处罚建议：{punishment_text}\n\n请列出审核要点，每条一句话。"),
    ]
)
