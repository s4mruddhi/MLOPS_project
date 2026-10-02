"""
Retrieval Metrics Evaluator.
Calculates Context Precision, Context Recall, Hit@K, MRR, and NDCG@K.
"""

import math
from typing import List
from benchmark.schema import DocumentChunk, RetrievalMetrics


class RetrievalEvaluator:
    """Computes quantitative retrieval quality metrics for a retrieved doc sequence against gold document IDs."""

    @staticmethod
    def compute_metrics(
        retrieved_chunks: List[DocumentChunk], gold_doc_ids: List[str], k: int = 3
    ) -> RetrievalMetrics:
        if not gold_doc_ids:
            return RetrievalMetrics(
                hit_rate_k=1.0, mrr=1.0, ndcg_k=1.0, context_precision=1.0, context_recall=1.0
            )

        retrieved_ids = [doc.doc_id for doc in retrieved_chunks[:k]]

        # 1. Hit Rate @ K
        hits = [doc_id for doc_id in retrieved_ids if doc_id in gold_doc_ids]
        hit_rate = 1.0 if len(hits) > 0 else 0.0

        # 2. Context Recall (proportion of relevant gold docs retrieved)
        unique_retrieved_gold = set(hits)
        context_recall = len(unique_retrieved_gold) / len(set(gold_doc_ids))

        # 3. Context Precision (weighted precision by rank)
        if not retrieved_ids:
            context_precision = 0.0
            mrr = 0.0
            ndcg = 0.0
        else:
            # MRR (Mean Reciprocal Rank)
            mrr = 0.0
            for rank_idx, doc_id in enumerate(retrieved_ids, start=1):
                if doc_id in gold_doc_ids:
                    mrr = 1.0 / rank_idx
                    break

            # Context Precision = sum(Precision@i * is_relevant(i)) / total_relevant_in_top_k
            relevant_seen = 0
            precision_sum = 0.0
            for rank_idx, doc_id in enumerate(retrieved_ids, start=1):
                if doc_id in gold_doc_ids:
                    relevant_seen += 1
                    precision_sum += relevant_seen / rank_idx

            context_precision = (
                precision_sum / len(hits) if len(hits) > 0 else 0.0
            )

            # NDCG @ K
            dcg = 0.0
            for rank_idx, doc_id in enumerate(retrieved_ids, start=1):
                rel = 1.0 if doc_id in gold_doc_ids else 0.0
                dcg += rel / math.log2(rank_idx + 1)

            idcg = 0.0
            for rank_idx in range(1, min(len(gold_doc_ids), k) + 1):
                idcg += 1.0 / math.log2(rank_idx + 1)

            ndcg = dcg / idcg if idcg > 0 else 0.0

        return RetrievalMetrics(
            hit_rate_k=hit_rate,
            mrr=mrr,
            ndcg_k=ndcg,
            context_precision=context_precision,
            context_recall=context_recall,
        )
