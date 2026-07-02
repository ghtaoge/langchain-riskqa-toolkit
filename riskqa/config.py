"""Global configuration for riskqa toolkit."""

import os
from typing import Literal

from pydantic import BaseModel, Field


class RiskQAConfig(BaseModel):
    """Configuration for LLM provider and scoring weights."""

    llm_provider: Literal["openai", "azure", "ollama", "custom"] = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str | None = Field(default_factory=lambda: os.getenv("RISKQA_API_KEY"))
    api_base: str | None = Field(default_factory=lambda: os.getenv("RISKQA_API_BASE"))
    temperature: float = 0.1
    max_tokens: int = 2048
    rule_weight: float = 0.4
    llm_weight: float = 0.6

    def get_llm(self):
        """Create and return an LLM instance based on provider config."""
        from langchain_openai import ChatOpenAI

        if self.llm_provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.llm_provider == "azure":
            from langchain_openai import AzureChatOpenAI

            return AzureChatOpenAI(
                azure_deployment=self.model_name,
                api_key=self.api_key,
                azure_endpoint=self.api_base or "",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.llm_provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=self.model_name,
                base_url=self.api_base or "http://localhost:11434",
                temperature=self.temperature,
            )
        elif self.llm_provider == "custom":
            return ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
