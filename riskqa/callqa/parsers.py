"""Output parsers for callqa chain results."""

from langchain_core.output_parsers import JsonOutputParser

from riskqa.core.schemas import CallQAReport

callqa_report_parser = JsonOutputParser(pydantic_object=CallQAReport)
