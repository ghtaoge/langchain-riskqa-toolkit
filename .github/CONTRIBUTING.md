# Contributing to riskqa-toolkit

Thank you for your interest in contributing!

## Development Setup

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check riskqa/ tests/
```

## Adding a New Module

1. Create `riskqa/<module>/` with `__init__.py`, `chains.py`, `prompts.py`, `parsers.py`, `rules.py`
2. Add schemas to `riskqa/core/schemas.py`
3. Add tests in `tests/test_<module>.py`
4. Add mock data in `data/mock_<module>/`
5. Update `riskqa/__init__.py` exports
6. Update README

## De-personalization Rules

- Never include real customer names, phone numbers, or addresses
- Never include internal API URLs or credentials
- Never include proprietary sensitive word lexicons
- Use placeholder data: `张先生`, `138****1234`, `产品A`
