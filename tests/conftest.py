"""Shared test fixtures and helpers."""

from langchain_community.chat_models.fake import FakeListChatModel


def make_fake_llm(responses: list[str]) -> FakeListChatModel:
    """Create a fake LLM that returns preset string responses in order.

    Each response is wrapped in an AIMessage by FakeListChatModel, making it
    compatible with LCEL chains (prompt | llm | StrOutputParser).
    """
    return FakeListChatModel(responses=responses)
