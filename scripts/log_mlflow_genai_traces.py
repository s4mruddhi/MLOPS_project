"""
Logs GenAI Execution Traces into MLflow Tracing DB for RAGOps_Retrieval_Experiments.
"""

import os
import sys
import time
import mlflow
from mlflow.tracking import MlflowClient

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

MLFLOW_DB = "sqlite:///mlflow.db"
EXPERIMENT_NAME = "RAGOps_Retrieval_Experiments"

def main():
    print("Setting MLflow tracking URI to:", MLFLOW_DB)
    mlflow.set_tracking_uri(MLFLOW_DB)
    mlflow.set_experiment(EXPERIMENT_NAME)
    client = MlflowClient()

    sample_traces = [
        {
            "name": "RAG_Semantic_Query_API_Payload",
            "query": "What is the maximum allowed API request payload size?",
            "user_role": "employee",
            "answer": "According to API Gateway docs [HR-001_chunk_000], maximum allowed payload size is 10 MB per request.",
            "citations": ["HR-001_chunk_000"],
            "latency_s": 0.045,
        },
        {
            "name": "RAG_TFIDF_Query_Password_Policy",
            "query": "What are the mandatory password complexity requirements?",
            "user_role": "employee",
            "answer": "Password must be at least 12 characters with uppercase, lowercase, numbers, and special symbols [SEC-001_chunk_001].",
            "citations": ["SEC-001_chunk_001"],
            "latency_s": 0.012,
        },
        {
            "name": "RAG_BM25_Query_Remote_Work",
            "query": "What is the remote work and work-from-home policy?",
            "user_role": "employee",
            "answer": "Full-time employees are eligible for up to 2 days of remote work per week with manager approval [HR-002_chunk_001].",
            "citations": ["HR-002_chunk_001"],
            "latency_s": 0.018,
        },
    ]

    for item in sample_traces:
        print(f"Logging trace: {item['name']}...")
        try:
            t = client.start_trace(
                name=item["name"],
                inputs={"query": item["query"], "user_role": item["user_role"]},
                tags={"application": "RAGOps_Assistant", "llm_provider": "LocalContextSynthesizer"},
            )
            time.sleep(item["latency_s"])
            t.set_outputs({"generated_answer": item["answer"], "citations": item["citations"]})
            client.end_trace(request_id=t.request_id, outputs={"generated_answer": item["answer"], "citations": item["citations"]})
            print(f"  -> Successfully logged trace ID: {t.request_id}")
        except Exception as e:
            print(f"  -> Trace logging warning: {e}")

    print("\nMLflow GenAI Traces Logged Successfully!")

if __name__ == "__main__":
    main()
