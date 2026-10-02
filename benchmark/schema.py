"""
Data schemas for the Agentic RAG Benchmark & Continuous Evaluation Framework.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class EntailmentStatus(str, Enum):
    ENTAILED = "entailed"         # Citation fully supports the claim
    CONTRADICTED = "contradicted" # Citation contradicts the claim
    UNSUPPORTED = "unsupported"   # Citation does not contain proof for claim
    MISSING_CITATION = "missing_citation" # Claim made without any citation


@dataclass
class DocumentChunk:
    doc_id: str
    text: str
    source_title: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0


@dataclass
class ToolCallTrace:
    tool_name: str
    input_args: Dict[str, Any]
    output: Any
    status: str  # "success" or "error"
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class CitationClaim:
    claim_text: str
    cited_doc_ids: List[str]
    entailment_status: EntailmentStatus = EntailmentStatus.UNSUPPORTED
    supporting_evidence: Optional[str] = None


@dataclass
class QuerySample:
    sample_id: str
    query: str
    category: str  # e.g., "single_doc", "multi_doc", "tool_augmented", "adversarial"
    gold_context_ids: List[str]
    gold_answer: str
    expected_tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    available_docs: List[DocumentChunk] = field(default_factory=list)


@dataclass
class AgentTrace:
    sample_id: str
    query: str
    retrieved_chunks: List[DocumentChunk]
    tool_calls: List[ToolCallTrace]
    generated_answer: str
    extracted_citations: List[CitationClaim]
    total_latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class RetrievalMetrics:
    hit_rate_k: float
    mrr: float
    ndcg_k: float
    context_precision: float
    context_recall: float


@dataclass
class CitationMetrics:
    citation_precision: float  # Supported claims / Total claims
    citation_recall: float     # Supported claims / Ground truth required claims
    unsupported_citation_rate: float # Unsupported citations / Total citations
    hallucination_rate: float  # Claims with 0 supporting context / Total claims


@dataclass
class ToolMetrics:
    tool_selection_accuracy: float
    param_match_rate: float
    tool_success_rate: float


@dataclass
class SampleEvaluationResult:
    sample_id: str
    query: str
    retrieval: RetrievalMetrics
    citation: CitationMetrics
    tool: ToolMetrics
    overall_correctness_score: float
    latency_ms: float
    has_hallucination: bool
    has_tool_failure: bool
