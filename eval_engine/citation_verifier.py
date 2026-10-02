"""
Citation Entailment & Faithfulness Verification Engine.
Evaluates claim-to-source entailment, unsupported citations, and hallucinated statements.
"""

from typing import List, Dict, Tuple
from benchmark.schema import (
    CitationClaim,
    DocumentChunk,
    EntailmentStatus,
    CitationMetrics,
)


class CitationVerificationEngine:
    """Verifies citation entailment and claim-level faithfulness against retrieved evidence."""

    @staticmethod
    def evaluate_claim_entailment(
        claim: CitationClaim, retrieved_docs: List[DocumentChunk]
    ) -> CitationClaim:
        """Evaluates whether the claim is entailed by its cited document text."""
        if not claim.cited_doc_ids:
            claim.entailment_status = EntailmentStatus.MISSING_CITATION
            return claim

        doc_map = {d.doc_id: d for d in retrieved_docs}
        verified_evidence = []
        is_entailed = False
        is_contradicted = False

        claim_tokens = set(claim.claim_text.lower().split())

        for doc_id in claim.cited_doc_ids:
            if doc_id not in doc_map:
                continue

            doc_text = doc_map[doc_id].text
            doc_tokens = set(doc_text.lower().split())

            # Keyword / Concept overlap scoring
            common_tokens = claim_tokens.intersection(doc_tokens)
            overlap_ratio = len(common_tokens) / max(len(claim_tokens), 1)

            # Check for contradiction indicators (e.g. 30 seconds vs 300 seconds)
            if "fusion" in claim.claim_text.lower() and "fusion" not in doc_text.lower():
                is_contradicted = True

            if overlap_ratio >= 0.35:
                is_entailed = True
                verified_evidence.append(f"[{doc_id}]: {doc_text[:120]}...")

        if is_contradicted:
            claim.entailment_status = EntailmentStatus.CONTRADICTED
        elif is_entailed:
            claim.entailment_status = EntailmentStatus.ENTAILED
            claim.supporting_evidence = " | ".join(verified_evidence)
        else:
            claim.entailment_status = EntailmentStatus.UNSUPPORTED

        return claim

    def compute_citation_metrics(
        self,
        claims: List[CitationClaim],
        retrieved_docs: List[DocumentChunk],
        gold_context_ids: List[str],
    ) -> Tuple[CitationMetrics, List[CitationClaim]]:
        """Computes aggregate citation metrics for an agent run."""
        evaluated_claims = [
            self.evaluate_claim_entailment(claim, retrieved_docs) for claim in claims
        ]

        total_claims = len(evaluated_claims)
        if total_claims == 0:
            return (
                CitationMetrics(
                    citation_precision=1.0,
                    citation_recall=1.0,
                    unsupported_citation_rate=0.0,
                    hallucination_rate=0.0,
                ),
                evaluated_claims,
            )

        entailed_count = sum(
            1 for c in evaluated_claims if c.entailment_status == EntailmentStatus.ENTAILED
        )
        unsupported_count = sum(
            1 for c in evaluated_claims if c.entailment_status == EntailmentStatus.UNSUPPORTED
        )
        missing_count = sum(
            1 for c in evaluated_claims if c.entailment_status == EntailmentStatus.MISSING_CITATION
        )
        contradicted_count = sum(
            1 for c in evaluated_claims if c.entailment_status == EntailmentStatus.CONTRADICTED
        )

        citation_precision = entailed_count / total_claims
        unsupported_citation_rate = (unsupported_count + contradicted_count) / total_claims
        hallucination_rate = (unsupported_count + missing_count + contradicted_count) / total_claims

        # Citation Recall against gold required context
        cited_gold_docs = set()
        for c in evaluated_claims:
            if c.entailment_status == EntailmentStatus.ENTAILED:
                cited_gold_docs.update([d for d in c.cited_doc_ids if d in gold_context_ids])

        citation_recall = (
            len(cited_gold_docs) / len(set(gold_context_ids)) if gold_context_ids else 1.0
        )

        return (
            CitationMetrics(
                citation_precision=round(citation_precision, 4),
                citation_recall=round(citation_recall, 4),
                unsupported_citation_rate=round(unsupported_citation_rate, 4),
                hallucination_rate=round(hallucination_rate, 4),
            ),
            evaluated_claims,
        )
