"""Pydantic schemas."""

from pydantic import BaseModel
from typing import Literal


class SourceCitation(BaseModel):
    """Reference to the source of an answer within a document."""
    page: int
    quote: str


class Answer(BaseModel):
    """Grounded answer to a single ESG question."""
    status: Literal["found", "not_found"]
    answer: str | None = None
    confidence: Literal["high", "medium", "low"] | None = None
    source: SourceCitation | None = None


class CompanyReport(BaseModel):
    """Full ESG analysis report for a single company."""
    company: str
    summary: str
    questions: dict[str, Answer]  # question text → Answer