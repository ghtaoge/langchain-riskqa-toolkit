"""Output parsers for violationqa chain results."""

from langchain_core.output_parsers import JsonOutputParser
from riskqa.core.schemas import ViolationQAReport

violationqa_report_parser = JsonOutputParser(pydantic_object=ViolationQAReport)
