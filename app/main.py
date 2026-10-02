"""
FastAPI Enterprise Knowledge Assistant (RAG Ops) REST Prediction Service.
"""

import os
import time
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from src.config import MODEL_ARTIFACT_DIR, RAW_DOCS_PATH, REFERENCE_QUERIES_PATH, MODEL_REGISTRY_NAME
from src.monitoring.drift_detector import DataDriftDetector
from src.responsible_ai.shap_explainer import SHAPExplainer
from rag_agent.agent import AgenticRAGAgent, AgentMode
from benchmark.schema import QuerySample, DocumentChunk
from app.schemas import (
    RAGQueryRequest,
    BatchRAGRequest,
    RAGQueryResponse,
    SourceChunkSchema,
    CitationClaimSchema,
    ExplanationResponse,
    HealthCheckResponse,
)

# Initialize FastAPI Application
app = FastAPI(
    title="Production-Ready Enterprise Knowledge Assistant (RAG Ops) REST API",
    description="Enterprise RAG Ops REST service with Prometheus metrics, claim-level NLI citation verification, and query drift detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse, tags=["Dashboard UI"])
def get_dashboard_ui():
    """Serves the Interactive Enterprise Knowledge Assistant & RAG Ops Dashboard UI."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Enterprise Knowledge Assistant RAG Service Running</h1>"


# Prometheus Metrics Collectors
REQUEST_COUNT = Counter("rag_http_requests_total", "Total RAG HTTP requests", ["endpoint", "status"])
ERROR_COUNT = Counter("rag_http_errors_total", "Total RAG HTTP errors", ["endpoint", "error_code"])
INFERENCE_LATENCY = Histogram("rag_query_latency_seconds", "RAG Query processing latency in seconds", ["endpoint"])
DATA_DRIFT_GAUGE = Gauge("rag_query_drift_ratio", "Query distribution drift ratio against baseline reference dataset")

# Global State Variables
MODEL_STATE = {
    "agent": None,
    "explainer": None,
    "drift_detector": None,
    "documents": [],
    "version": "v1.0.0",
}


def load_artifacts():
    """Loads RAG Agent, Document Corpus, and Reference Baseline artifacts into memory."""
    MODEL_STATE["agent"] = AgenticRAGAgent(mode=AgentMode.ACCURATE)
    MODEL_STATE["explainer"] = SHAPExplainer()

    import json
    if os.path.exists(RAW_DOCS_PATH):
        with open(RAW_DOCS_PATH, "r", encoding="utf-8") as f:
            MODEL_STATE["documents"] = json.load(f)

    if os.path.exists(REFERENCE_QUERIES_PATH):
        ref_df = pd.read_csv(REFERENCE_QUERIES_PATH)
        MODEL_STATE["drift_detector"] = DataDriftDetector(ref_df)
    else:
        ref_df = pd.DataFrame([{"query_text": "What is the API Gateway payload limit?"}])
        MODEL_STATE["drift_detector"] = DataDriftDetector(ref_df)

    print(f"[FastAPI] Loaded RAG Agent and {len(MODEL_STATE['documents'])} Knowledge Documents.")


@app.on_event("startup")
def startup_event():
    load_artifacts()


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """Liveness probe health-check endpoint."""
    is_loaded = MODEL_STATE["agent"] is not None
    return HealthCheckResponse(
        status="HEALTHY" if is_loaded else "DEGRADED",
        model_loaded=is_loaded,
        model_name=MODEL_REGISTRY_NAME,
        version=MODEL_STATE["version"],
    )


@app.get("/ready", tags=["Health"])
def readiness_check():
    """Readiness probe endpoint."""
    if MODEL_STATE["agent"] is None:
        raise HTTPException(status_code=503, detail="Service not ready: RAG artifacts uninitialized.")
    return {"status": "READY", "timestamp": time.time()}


@app.get("/model-info", tags=["Metadata"])
def get_model_info():
    """Returns metadata for the active registered production RAG assistant."""
    if MODEL_STATE["agent"] is None:
        load_artifacts()
    return {
        "model_name": MODEL_REGISTRY_NAME,
        "agent_mode": MODEL_STATE["agent"].mode,
        "version": MODEL_STATE["version"],
        "alias": "Production",
        "num_documents": len(MODEL_STATE["documents"]),
    }


def execute_rag_query(request: RAGQueryRequest) -> Tuple[RAGQueryResponse, Any]:
    start_time = time.perf_counter()

    if MODEL_STATE["agent"] is None:
        load_artifacts()

    # Convert documents to DocumentChunk schema
    candidate_chunks = [
        DocumentChunk(
            doc_id=d.get("doc_id", f"DOC-{idx}"),
            source_title=d.get("source_title", "General Policy"),
            text=d.get("text", ""),
            score=0.90 - idx * 0.05,
        )
        for idx, d in enumerate(MODEL_STATE["documents"])
    ]

    sample = QuerySample(
        sample_id="REQ-LIVE",
        query=request.query,
        category="live_user_query",
        gold_context_ids=["DOC-GATEWAY-101", "DOC-SEC-201"],
        gold_answer="",
        available_docs=candidate_chunks,
    )

    trace = MODEL_STATE["agent"].execute(sample)

    sources = [
        SourceChunkSchema(
            doc_id=c.doc_id,
            source_title=c.source_title,
            text_snippet=c.text[:120] + "...",
            score=round(c.score, 4),
        )
        for c in trace.retrieved_chunks[:request.top_k]
    ]

    citations = [
        CitationClaimSchema(
            claim_text=c.claim_text,
            cited_doc_ids=c.cited_doc_ids,
            entailment_status=c.entailment_status.value,
        )
        for c in trace.extracted_citations
    ]

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    response = RAGQueryResponse(
        query=request.query,
        generated_answer=trace.generated_answer,
        retrieved_sources=sources,
        extracted_citations=citations,
        latency_ms=round(elapsed_ms, 2),
        confidence_score=0.92,
        model_version=MODEL_STATE["version"],
    )

    return response, trace


@app.post("/predict", response_model=RAGQueryResponse, tags=["RAG Assistant"])
@app.post("/ask", response_model=RAGQueryResponse, tags=["RAG Assistant"])
def ask_question(request: RAGQueryRequest):
    """Processes an enterprise knowledge query and returns answer with inline citations."""
    try:
        with INFERENCE_LATENCY.labels(endpoint="/ask").time():
            res, _ = execute_rag_query(request)
            REQUEST_COUNT.labels(endpoint="/ask", status="200").inc()
            return res
    except Exception as e:
        ERROR_COUNT.labels(endpoint="/ask", error_code="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-batch", tags=["RAG Assistant"])
def ask_batch(batch: BatchRAGRequest):
    """Batch RAG query endpoint."""
    try:
        results = []
        for req in batch.queries:
            res, _ = execute_rag_query(req)
            results.append(res)
        REQUEST_COUNT.labels(endpoint="/predict-batch", status="200").inc()
        return {"total_queries": len(results), "responses": results}
    except Exception as e:
        ERROR_COUNT.labels(endpoint="/predict-batch", error_code="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", response_model=ExplanationResponse, tags=["Explainability"])
def explain_rag_answer(request: RAGQueryRequest):
    """Generates NLI claim-level citation verification & attribution explanation for RAG answer."""
    res, trace = execute_rag_query(request)
    explanation = MODEL_STATE["explainer"].explain_instance(
        query=request.query,
        answer=res.generated_answer,
        claims=trace.extracted_citations,
        retrieved_docs=trace.retrieved_chunks,
    )

    return ExplanationResponse(
        query=request.query,
        generated_answer=res.generated_answer,
        citation_precision=explanation["citation_precision"],
        unsupported_rate=explanation["unsupported_rate"],
        claim_attributions=explanation["claim_attributions"],
    )


@app.post("/drift-check", tags=["Monitoring"])
def check_query_drift(batch: BatchRAGRequest):
    """Calculates query distribution drift for incoming batch of user queries."""
    if MODEL_STATE["drift_detector"] is None:
        load_artifacts()

    df_batch = pd.DataFrame([{"query_text": q.query} for q in batch.queries])
    drift_result = MODEL_STATE["drift_detector"].detect_feature_drift(df_batch)

    DATA_DRIFT_GAUGE.set(drift_result["overall_drift_ratio"])
    return drift_result


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus metrics scraper endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
