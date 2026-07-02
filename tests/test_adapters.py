"""Tests for data input adapters."""

import json
import tempfile

from riskqa.core.adapters import DataAdapter
from riskqa.core.schemas import CallTranscript, ChatSession, WorkOrder


def test_from_json_call_transcript():
    data = {
        "call_id": "call-001",
        "duration_seconds": 120,
        "fragments": [
            {"speaker": "agent", "start_time": 0, "end_time": 10, "text": "您好"},
            {"speaker": "customer", "start_time": 10, "end_time": 20, "text": "咨询"},
        ],
    }
    result = DataAdapter.from_json(data, CallTranscript)
    assert isinstance(result, CallTranscript)
    assert result.call_id == "call-001"


def test_from_json_chat_session():
    data = {
        "session_id": "chat-001",
        "messages": [
            {"sender": "agent", "timestamp": "2026-01-01T10:00:00", "content": "您好"},
        ],
    }
    result = DataAdapter.from_json(data, ChatSession)
    assert isinstance(result, ChatSession)
    assert result.session_id == "chat-001"


def test_from_json_work_order():
    data = {
        "order_id": "WO-001",
        "title": "售后问题",
        "description": "客户反馈问题",
        "customer_messages": ["产品有问题"],
    }
    result = DataAdapter.from_json(data, WorkOrder)
    assert isinstance(result, WorkOrder)
    assert result.order_id == "WO-001"


def test_from_json_file():
    data = {"call_id": "call-002", "duration_seconds": 60, "fragments": []}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        result = DataAdapter.from_json_file(f.name, CallTranscript)
    assert result.call_id == "call-002"


def test_from_json_invalid():
    data = {"invalid": "data"}
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DataAdapter.from_json(data, CallTranscript)
