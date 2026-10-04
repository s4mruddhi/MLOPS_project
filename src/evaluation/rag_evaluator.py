"""
RAG Evaluator & Failure Attribution Diagnostic Engine.
Measures Groundedness, Answer Relevance, Citation Correctness, and Failure Attribution.
"""

import os
import re
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from src.generation.llm_client import FALLBACK_MESSAGE

def calculate_groundedness(answer: str, retrieved_chunks: List[Dict[str, Any]]) -> float:
    """Calculates proportion of answer claims supported by retrieved chunk texts."""
    if answer == FALLBACK_MESSAGE:
        return 1.0
        
    if not retrieved_chunks or not answer.strip():
        return 0.0

    context_text = " ".join([c.get("text", "") for c in retrieved_chunks]).lower()
    
    # Strip citation tags like [HR-001_chunk_000] for claim checking
    clean_answer = re.sub(r"\[[A-Z0-9_-]+_chunk_\d+\]", "", answer).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_answer) if len(s.strip()) > 10]
    
    if not sentences:
        return 1.0

    supported_count = 0
    for s in sentences:
        s_words = set(re.findall(r"\w+", s.lower())) - {"the", "a", "an", "is", "are", "to", "in", "of", "and", "or", "for", "by", "with", "this", "that", "policy"}
        if not s_words:
            supported_count += 1
            continue
            
        matched_words = sum(1 for w in s_words if w in context_text)
        match_ratio = matched_words / len(s_words)
        if match_ratio >= 0.5:
            supported_count += 1

    return round(supported_count / len(sentences), 4)

def calculate_answer_relevance(answer: str, reference_answer: str, question: str) -> float:
    """Calculates word overlap relevance between generated answer, reference answer, and question."""
    if answer == FALLBACK_MESSAGE:
        return 1.0 if reference_answer == FALLBACK_MESSAGE else 0.0

    ans_words = set(re.findall(r"\w+", answer.lower()))
    ref_words = set(re.findall(r"\w+", reference_answer.lower())) - {"the", "a", "an", "is", "are", "in", "of", "to"}
    
    if not ref_words:
        return 1.0

    overlap = len(ans_words & ref_words)
    return round(overlap / len(ref_words), 4)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "evaluation", "rag_questions.jsonl")

class RAGEvaluator:
    """Evaluates full RAG pipeline and performs Retrieval-vs-Generation Failure Attribution."""

    def __init__(self, dataset_path: str = DEFAULT_DATASET_PATH):
        self.dataset_path = dataset_path
        self.questions = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.questions.append(json.loads(line))

    def classify_failure(self, 
                         q_record: Dict[str, Any], 
                         rag_response: Dict[str, Any]) -> str:
        """
        Classifies failure into one of 6 mutually exclusive diagnostic states:
        1. SUPPORTED_ANSWER
        2. RETRIEVAL_FAILURE
        3. INSUFFICIENT_CONTEXT
        4. GENERATION_FAILURE
        5. CITATION_FAILURE
        6. KNOWLEDGE_GAP
        """
        expected_docs = set(q_record.get("expected_document_ids", []))
        answerable = q_record.get("answerable", True)
        answer = rag_response["answer"]
        citations = rag_response.get("citations", [])
        retrieved_docs = set([d["document_id"] for d in rag_response.get("retrieved_documents", [])])
        
        # State 6: KNOWLEDGE_GAP / Unanswerable
        if not answerable or not expected_docs:
            if answer == FALLBACK_MESSAGE:
                return "KNOWLEDGE_GAP"
            else:
                return "GENERATION_FAILURE"

        # State 2: RETRIEVAL_FAILURE (expected document not retrieved)
        if not (expected_docs & retrieved_docs):
            return "RETRIEVAL_FAILURE"

        # State 3: INSUFFICIENT_CONTEXT (retrieved, but similarity score low)
        max_score = max([d.get("score", 0.0) for d in rag_response.get("retrieved_documents", [])], default=0.0)
        if max_score < 0.30:
            return "INSUFFICIENT_CONTEXT"

        # State 4: GENERATION_FAILURE (groundedness < 0.60)
        chunks = [{"text": d.get("text", ""), "score": d.get("score", 1.0)} for d in rag_response.get("retrieved_documents", [])]
        # Build full chunks with text from retrieved_documents if present
        groundedness = calculate_groundedness(answer, rag_response.get("retrieved_documents", []))
        if groundedness < 0.60:
            return "GENERATION_FAILURE"

        # State 5: CITATION_FAILURE (answer given but citations missing or unverified)
        if answer != FALLBACK_MESSAGE and not citations:
            return "CITATION_FAILURE"

        # State 1: SUPPORTED_ANSWER
        return "SUPPORTED_ANSWER"

    def evaluate_rag_pipeline(self, rag_generator) -> Dict[str, Any]:
        groundedness_list = []
        relevance_list = []
        citation_correct_list = []
        unsupported_rate_list = []
        
        attribution_counts = {
            "SUPPORTED_ANSWER": 0,
            "RETRIEVAL_FAILURE": 0,
            "INSUFFICIENT_CONTEXT": 0,
            "GENERATION_FAILURE": 0,
            "CITATION_FAILURE": 0,
            "KNOWLEDGE_GAP": 0
        }
        
        detailed_evaluations = []

        for q in self.questions:
            q_id = q["question_id"]
            query = q["question"]
            ref_answer = q.get("reference_answer", "")
            role = q.get("required_access_level", "employee")
            
            resp = rag_generator.generate_response(query=query, user_role=role, top_k=3)
            
            # Groundedness
            groundedness = calculate_groundedness(resp["answer"], resp["retrieved_documents"])
            groundedness_list.append(groundedness)
            unsupported_rate_list.append(1.0 - groundedness)
            
            # Answer Relevance
            relevance = calculate_answer_relevance(resp["answer"], ref_answer, query)
            relevance_list.append(relevance)
            
            # Citation Correctness
            has_citations = len(resp["citations"]) > 0 if resp["answer"] != FALLBACK_MESSAGE else True
            citation_correct_list.append(1.0 if has_citations else 0.0)
            
            # Failure Attribution
            diagnostic_state = self.classify_failure(q, resp)
            attribution_counts[diagnostic_state] += 1
            
            detailed_evaluations.append({
                "question_id": q_id,
                "category": q.get("category", "general"),
                "question": query,
                "answer": resp["answer"],
                "citations": resp["citations"],
                "groundedness_score": groundedness,
                "relevance_score": relevance,
                "diagnostic_state": diagnostic_state
            })

        total_q = len(self.questions)
        summary_metrics = {
            "total_questions_evaluated": total_q,
            "mean_groundedness_score": round(float(np.mean(groundedness_list)), 4),
            "mean_answer_relevance": round(float(np.mean(relevance_list)), 4),
            "citation_correctness_rate": round(float(np.mean(citation_correct_list)), 4),
            "unsupported_claim_rate": round(float(np.mean(unsupported_rate_list)), 4),
            "failure_attribution": attribution_counts,
            "detailed_evaluations": detailed_evaluations
        }
        
        return summary_metrics
