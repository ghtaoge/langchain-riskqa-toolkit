"""Tests for RiskQAConfig."""

import os

from riskqa.config import RiskQAConfig


def test_default_config():
    config = RiskQAConfig()
    assert config.llm_provider == "openai"
    assert config.model_name == "gpt-4o-mini"
    assert config.temperature == 0.1
    assert config.rule_weight == 0.4
    assert config.llm_weight == 0.6


def test_custom_config():
    config = RiskQAConfig(
        llm_provider="ollama",
        model_name="llama3",
        api_base="http://localhost:11434",
        temperature=0.0,
        rule_weight=0.5,
        llm_weight=0.5,
    )
    assert config.llm_provider == "ollama"
    assert config.model_name == "llama3"
    assert config.temperature == 0.0


def test_config_reads_env():
    os.environ["RISKQA_API_KEY"] = "test-key-123"
    config = RiskQAConfig()
    assert config.api_key == "test-key-123"
    del os.environ["RISKQA_API_KEY"]


def test_invalid_provider():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        RiskQAConfig(llm_provider="invalid_provider")
