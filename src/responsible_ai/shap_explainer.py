"""
RAG Citation Attribution & Explainability Engine.
Generates claim-level source attributions and evidence explanations for answers.
"""

from typing import Dict, Any, List
from benchmark.schema import CitationClaim, DocumentChunk
from eval_engine.citation_verifier import CitationVerificationEngine


class SHAPExplainer:
    """Provides claim attribution and source chunk explainability for RAG answers."""

    def __init__(self, model: Any = None, feature_names: List[str] = None):
        self.verifier = CitationVerificationEngine()

    def explain_instance(
        self, query: str, answer: str, claims: List[CitationClaim], retrieved_docs: List[DocumentChunk]
    ) -> Dict[str, Any]:
        """Calculates evidence attributions for each claim in generated answer."""
        metrics, evaluated_claims = self.verifier.compute_citation_metrics(
            claims=claims, retrieved_docs=retrieved_docs, gold_context_ids=[]
        )

        attributions = {}
        for c in evaluated_claims:
            doc_str = ", ".join(c.cited_doc_ids) if c.cited_doc_ids else "No Citation"
            attributions[c.claim_text[:50] + "..."] = f"Status: {c.entailment_status.value} [{doc_str}]"

        return {
            "citation_precision": metrics.citation_precision,
            "unsupported_rate": metrics.unsupported_citation_rate,
            "claim_attributions": attributions,
            "top_positive_features": {
                c.claim_text[:40]: 1.0 if c.entailment_status.value == "entailed" else -0.5
                for c in evaluated_claims
            },
        }
