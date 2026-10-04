"""
Full RAG Generation Pipeline with Versioned Prompts and Citation Verification.
"""

import os
import time
from typing import List, Dict, Any, Optional
import mlflow
from src.retrieval.retrieval_manager import RetrievalManager
from src.generation.llm_client import LLMClient, FALLBACK_MESSAGE

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")

def load_prompt_template(filename: str) -> str:
    filepath = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

class RAGGenerator:
    """Full RAG Generation Pipeline with Prompt Versioning and Citation Verification."""

    def __init__(self, 
                 retrieval_manager: Optional[RetrievalManager] = None,
                 system_prompt_version: str = "system_v1.txt",
                 answer_prompt_version: str = "answer_v1.txt"):
        self.retrieval_manager = retrieval_manager or RetrievalManager()
        self.system_prompt_version = system_prompt_version
        self.answer_prompt_version = answer_prompt_version
        
        self.system_prompt = load_prompt_template(system_prompt_version)
        self.answer_template = load_prompt_template(answer_prompt_version)
        self.llm_client = LLMClient()

    @mlflow.trace(name="RAGOps_Query_Generation", span_type="CHAIN")
    def generate_response(self, 
                          query: str, 
                          user_role: str = "employee", 
                          retrieval_method: str = "semantic", 
                          top_k: int = 3) -> Dict[str, Any]:
        pipeline_start = time.time()
        
        # 1. Retrieval Layer with Access Control
        retrieval_start = time.time()
        retrieved_chunks = self.retrieval_manager.retrieve(
            query_text=query,
            method=retrieval_method,
            top_k=top_k,
            user_role=user_role
        )
        retrieval_latency = round(time.time() - retrieval_start, 6)
        
        # 2. LLM / Synthesizer Generation
        answer, citations, gen_latency, provider = self.llm_client.generate(
            query=query,
            retrieved_chunks=retrieved_chunks,
            system_prompt=self.system_prompt,
            answer_template=self.answer_template
        )
        
        total_latency = round(time.time() - pipeline_start, 6)
        
        # 3. Verify Citations against retrieved chunks
        valid_chunk_ids = set(c["chunk_id"] for c in retrieved_chunks)
        verified_citations = [c for c in citations if c in valid_chunk_ids]
        
        response = {
            "query": query,
            "answer": answer,
            "citations": verified_citations,
            "retrieved_documents": [
                {
                    "chunk_id": c["chunk_id"],
                    "document_id": c["document_id"],
                    "score": c["score"],
                    "text": c.get("text", ""),
                    "access_level": c["metadata"].get("access_level", "employee")
                }
                for c in retrieved_chunks
            ],
            "retrieval_latency": retrieval_latency,
            "generation_latency": gen_latency,
            "total_latency": total_latency,
            "prompt_version": f"{self.system_prompt_version} + {self.answer_prompt_version}",
            "retrieval_version": f"{retrieval_method}_v1",
            "document_version": "27_docs_v1",
            "application_version": "1.0.0",
            "llm_provider": provider
        }
        
        return response
