"""
Agentic RAG System Simulator.
Simulates production agent reasoning, retrieval, tool calls, and response generation with citations.
Supports configurable agent behavior modes for regression and evaluation benchmarking.
"""

import re
import time
from typing import List, Optional
from benchmark.schema import (
    QuerySample,
    AgentTrace,
    DocumentChunk,
    ToolCallTrace,
    CitationClaim,
    EntailmentStatus,
)
from rag_agent.retriever import VectorRetriever
from rag_agent.tool_executor import MockToolRegistry


class AgentMode:
    ACCURATE = "accurate"             # Gold baseline behavior
    HALLUCINATING = "hallucinating"   # Generates unsupported claims / missing citations
    RETRIEVAL_FAIL = "retrieval_fail" # Uses noisy/irrelevant context
    TOOL_FAIL = "tool_fail"           # Uses wrong tool or invalid args


class AgenticRAGAgent:
    """Agentic RAG system execution runner."""

    def __init__(self, mode: str = AgentMode.ACCURATE, top_k: int = 3):
        self.mode = mode
        self.retriever = VectorRetriever(top_k=top_k)
        self.tool_executor = MockToolRegistry()

    def extract_citations_from_text(self, text: str) -> List[CitationClaim]:
        """Parses answer text into individual claims and cited document IDs."""
        claims = []
        # Split text into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

        for sentence in sentences:
            # Find citation brackets like [DOC-XXX-101] or [DOC-1, DOC-2]
            found_docs = re.findall(r'\[([A-Z0-9\-_,\s]+)\]', sentence)
            doc_ids = []
            if found_docs:
                for match in found_docs:
                    doc_ids.extend([d.strip() for d in match.split(',')])

            # Strip citation tags from sentence to isolate pure claim text
            clean_claim = re.sub(r'\[[A-Z0-9\-_,\s]+\]', '', sentence).strip()

            claims.append(
                CitationClaim(
                    claim_text=clean_claim,
                    cited_doc_ids=doc_ids,
                    entailment_status=EntailmentStatus.UNSUPPORTED,
                )
            )

        return claims

    def execute(self, sample: QuerySample) -> AgentTrace:
        start_time = time.perf_counter()

        # 1. Retrieval Step
        inject_noise = (self.mode == AgentMode.RETRIEVAL_FAIL)
        retrieved_docs = self.retriever.retrieve(
            query=sample.query,
            candidate_docs=sample.available_docs,
            inject_noise=inject_noise,
        )

        # 2. Tool Execution Step (if expected or mode dictated)
        tool_traces: List[ToolCallTrace] = []
        if sample.expected_tool_calls:
            for spec in sample.expected_tool_calls:
                tool_name = spec["tool_name"]
                args = spec["input_args"]

                if self.mode == AgentMode.TOOL_FAIL:
                    # Inject faulty tool call parameter or wrong tool
                    tool_name = "unknown_invalid_tool"
                    args = {"invalid_param": 999}

                trace = self.tool_executor.execute_tool(tool_name, args)
                tool_traces.append(trace)

        # 3. Answer & Citation Generation Step
        if self.mode == AgentMode.ACCURATE:
            if sample.gold_answer:
                answer = sample.gold_answer
            elif retrieved_docs:
                top_doc = retrieved_docs[0]
                answer = f"According to {top_doc.source_title}, {top_doc.text} [{top_doc.doc_id}]."
            else:
                answer = "No relevant context found in enterprise knowledge base."
        elif self.mode == AgentMode.HALLUCINATING:
            # Inject an extra unsupported claim without proper citation or with wrong citation
            answer = sample.gold_answer + " Additionally, our data centers are 100% powered by nuclear fusion reactors [DOC-GATEWAY-102]."
        elif self.mode == AgentMode.RETRIEVAL_FAIL:
            answer = "Based on retrieved docs, we recommend a 300 second idle timeout [DOC-PG-OLD-2021]."
        elif self.mode == AgentMode.TOOL_FAIL:
            answer = "Unable to fetch cluster metrics due to an internal system error."
        else:
            answer = sample.gold_answer

        # 4. Extract telemetry and citations
        extracted_citations = self.extract_citations_from_text(answer)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AgentTrace(
            sample_id=sample.sample_id,
            query=sample.query,
            retrieved_chunks=retrieved_docs,
            tool_calls=tool_traces,
            generated_answer=answer,
            extracted_citations=extracted_citations,
            total_latency_ms=elapsed_ms,
            prompt_tokens=len(sample.query.split()) * 4 + 120,
            completion_tokens=len(answer.split()) * 4,
        )
