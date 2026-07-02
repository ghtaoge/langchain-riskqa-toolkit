# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-02

### Added

- **callqa** module: phone call quality inspection with rule engine + LLM compliance analysis
- **chatqa** module: chat compliance inspection with topic extraction + sensitive detection
- **ticketqa** module: work order intelligence with classification + risk assessment
- **violationqa** module: violation ticket processing with severity grading + punishment suggestions
- **core** infrastructure: shared schemas, rule engine, scoring aggregator, data adapters
- Pydantic-based structured output for all modules
- Multi-provider LLM support (OpenAI, Azure, Ollama, custom)
- De-personalized mock data for all four scenarios
- Integration test: callqa → violationqa full pipeline
- CI workflow (GitHub Actions) with Python 3.11/3.12 matrix
- CONTRIBUTING guide with de-personalization rules
