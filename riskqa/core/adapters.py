"""Data input adapters — load transcripts, sessions, and work orders from JSON/CSV."""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class DataAdapter:
    """Convert raw data dicts or files into riskqa Pydantic models."""

    @staticmethod
    def from_json(data: dict, model_type: type[T]) -> T:
        """Parse a JSON dict into a Pydantic model instance."""
        return model_type.model_validate(data)

    @staticmethod
    def from_json_file(path: str | Path, model_type: type[T]) -> T:
        """Read a JSON file and parse into a Pydantic model instance."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return DataAdapter.from_json(data, model_type)
