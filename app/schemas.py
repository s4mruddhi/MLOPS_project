"""
FastAPI Request & Response Data Validation Schemas for Enterprise RAG Assistant.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="What is the maximum allowed API request payload size?", description="Enterprise knowledge query")
    top_k: int = Field(default=3, ge=1, le=10, description="Top-K documents to retrieve")
    include_citations: bool = Field(default=True, description="Whether to include inline citations [DOC-XXX]")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query string cannot be empty")
        return v


class BatchRAGRequest(BaseModel):
    queries: List[RAGQueryRequest]


class SourceChunkSchema(BaseModel):
    doc_id: str
    source_title: str
    text_snippet: str
    score: float


class CitationClaimSchema(BaseModel):
    claim_text: str
    cited_doc_ids: List[str]
    entailment_status: str


class RAGQueryResponse(BaseModel):
    query: str
    generated_answer: str
    retrieved_sources: List[SourceChunkSchema]
    extracted_citations: List[CitationClaimSchema]
    latency_ms: float
    confidence_score: float
    model_version: str


class ExplanationResponse(BaseModel):
    query: str
    generated_answer: str
    citation_precision: float
    unsupported_rate: float
    claim_attributions: Dict[str, str]


class HealthCheckResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    version: str
