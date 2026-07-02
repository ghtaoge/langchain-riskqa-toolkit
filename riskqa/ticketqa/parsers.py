"""Output parsers for ticketqa chain results."""

from langchain_core.output_parsers import JsonOutputParser

from riskqa.core.schemas import TicketQAReport

ticketqa_report_parser = JsonOutputParser(pydantic_object=TicketQAReport)
