"""Output parsers for chatqa chain results."""

from langchain_core.output_parsers import JsonOutputParser
from riskqa.core.schemas import ChatQAReport

chatqa_report_parser = JsonOutputParser(pydantic_object=ChatQAReport)
