"""
FastAPI Enterprise REST Prediction Service & Prometheus Monitoring Endpoint.
"""

import os
import time
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from src.config import MODEL_ARTIFACT_DIR, RAW_DATA_PATH, REFERENCE_DATA_PATH, MODEL_REGISTRY_NAME
from src.data.preprocessing import preprocess_data, FEATURE_COLUMNS
from src.monitoring.drift_detector import DataDriftDetector
from src.responsible_ai.shap_explainer import SHAPExplainer
from app.schemas import (
    CustomerInputSchema,
    BatchPredictionRequest,
    SinglePredictionResponse,
    ExplanationResponse,
    HealthCheckResponse,
)

# Initialize FastAPI Application
app = FastAPI(
    title="Enterprise Customer Churn Prediction REST API",
    description="Production-grade MLOps REST service with Prometheus metrics, SHAP explainability, and drift detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics Collectors
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
ERROR_COUNT = Counter("http_errors_total", "Total HTTP errors", ["endpoint", "error_code"])
INFERENCE_LATENCY = Histogram("model_inference_latency_seconds", "Model inference latency in seconds", ["endpoint"])
PREDICTION_COUNTER = Counter("model_predictions_total", "Model prediction outcome counts", ["risk_level"])
DATA_DRIFT_GAUGE = Gauge("model_data_drift_ratio", "Data drift ratio against reference dataset")

# Global State Variables
MODEL_STATE = {
    "model": None,
    "preprocessor": None,
    "feature_names": None,
    "reference_df": None,
    "explainer": None,
    "drift_detector": None,
    "version": "v1.0.0",
}


def load_artifacts():
    """Loads trained model, preprocessor, and reference data artifacts into memory."""
    model_path = os.path.join(MODEL_ARTIFACT_DIR, "best_model.pkl")
    prep_path = os.path.join(MODEL_ARTIFACT_DIR, "preprocessor.pkl")
    feat_path = os.path.join(MODEL_ARTIFACT_DIR, "feature_names.pkl")

    if os.path.exists(model_path) and os.path.exists(prep_path):
        MODEL_STATE["model"] = joblib.load(model_path)
        MODEL_STATE["preprocessor"] = joblib.load(prep_path)
        MODEL_STATE["feature_names"] = joblib.load(feat_path) if os.path.exists(feat_path) else FEATURE_COLUMNS
        MODEL_STATE["explainer"] = SHAPExplainer(MODEL_STATE["model"], MODEL_STATE["feature_names"])
        print("[FastAPI] Successfully loaded Model and Preprocessor artifacts.")
    else:
        print("[FastAPI WARNING] Artifacts not found. Run training pipeline first.")

    ref_path = REFERENCE_DATA_PATH if os.path.exists(REFERENCE_DATA_PATH) else RAW_DATA_PATH
    if os.path.exists(ref_path):
        ref_df = pd.read_csv(ref_path)
        MODEL_STATE["reference_df"] = ref_df
        MODEL_STATE["drift_detector"] = DataDriftDetector(ref_df)
        print(f"[FastAPI] Loaded reference baseline data ({len(ref_df)} samples).")


@app.on_event("startup")
def startup_event():
    load_artifacts()


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """Liveness probe health-check endpoint."""
    is_loaded = MODEL_STATE["model"] is not None
    return HealthCheckResponse(
        status="HEALTHY" if is_loaded else "DEGRADED",
        model_loaded=is_loaded,
        model_name=MODEL_REGISTRY_NAME,
        version=MODEL_STATE["version"],
    )


@app.get("/ready", tags=["Health"])
def readiness_check():
    """Readiness probe endpoint for Kubernetes / Load Balancer."""
    if MODEL_STATE["model"] is None or MODEL_STATE["preprocessor"] is None:
        raise HTTPException(status_code=503, detail="Service not ready: Model artifacts uninitialized.")
    return {"status": "READY", "timestamp": time.time()}


@app.get("/model-info", tags=["Metadata"])
def get_model_info():
    """Returns metadata for the active registered production model."""
    if MODEL_STATE["model"] is None:
        load_artifacts()
    if MODEL_STATE["model"] is None:
        raise HTTPException(status_code=404, detail="Model not initialized.")

    model_obj = MODEL_STATE["model"]
    return {
        "model_name": MODEL_REGISTRY_NAME,
        "model_type": type(model_obj).__name__,
        "version": MODEL_STATE["version"],
        "alias": "Production",
        "num_features": len(MODEL_STATE["feature_names"]),
        "features": MODEL_STATE["feature_names"],
    }


def predict_single_customer(customer: CustomerInputSchema) -> Tuple[int, float, str, float]:
    start_time = time.perf_counter()

    if MODEL_STATE["model"] is None or MODEL_STATE["preprocessor"] is None:
        load_artifacts()
        if MODEL_STATE["model"] is None:
            raise HTTPException(status_code=503, detail="Model artifact missing. Run training pipeline.")

    # Convert Pydantic model to DataFrame
    raw_dict = customer.model_dump()
    df_single = pd.DataFrame([raw_dict])

    # Transform features using fitted preprocessor
    X_trans, _, _, _ = preprocess_data(
        df_single, preprocessor=MODEL_STATE["preprocessor"], fit=False, save_path=None
    )

    # Inference prediction
    model = MODEL_STATE["model"]
    prob = float(model.predict_proba(X_trans)[0][1])
    pred = int(prob >= 0.50)

    if prob < 0.35:
        risk_level = "LOW"
    elif prob < 0.65:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Record Prometheus metrics
    PREDICTION_COUNTER.labels(risk_level=risk_level).inc()

    return pred, round(prob, 4), risk_level, round(elapsed_ms, 2)


@app.post("/predict", response_model=SinglePredictionResponse, tags=["Prediction"])
def predict(customer: CustomerInputSchema):
    """Predicts customer churn probability and risk level for a single customer record."""
    try:
        with INFERENCE_LATENCY.labels(endpoint="/predict").time():
            pred, prob, risk, latency = predict_single_customer(customer)
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()

            return SinglePredictionResponse(
                customer_id=customer.customer_id,
                prediction=pred,
                churn_probability=prob,
                risk_level=risk,
                latency_ms=latency,
                model_version=MODEL_STATE["version"],
            )
    except Exception as e:
        ERROR_COUNT.labels(endpoint="/predict", error_code="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-batch", tags=["Prediction"])
def predict_batch(batch: BatchPredictionRequest):
    """Batch prediction endpoint for array of customer records."""
    try:
        results = []
        for cust in batch.customers:
            pred, prob, risk, latency = predict_single_customer(cust)
            results.append(
                {
                    "customer_id": cust.customer_id,
                    "prediction": pred,
                    "churn_probability": prob,
                    "risk_level": risk,
                    "latency_ms": latency,
                }
            )
        REQUEST_COUNT.labels(method="POST", endpoint="/predict-batch", status="200").inc()
        return {"total_records": len(results), "predictions": results}
    except Exception as e:
        ERROR_COUNT.labels(endpoint="/predict-batch", error_code="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", response_model=ExplanationResponse, tags=["Explainability"])
def explain_prediction(customer: CustomerInputSchema):
    """Generates SHAP feature attribution explanation for a customer prediction."""
    if MODEL_STATE["explainer"] is None:
        load_artifacts()

    pred, prob, risk, _ = predict_single_customer(customer)

    df_single = pd.DataFrame([customer.model_dump()])
    X_trans, _, _, _ = preprocess_data(
        df_single, preprocessor=MODEL_STATE["preprocessor"], fit=False, save_path=None
    )

    explanation = MODEL_STATE["explainer"].explain_instance(X_trans)

    return ExplanationResponse(
        customer_id=customer.customer_id,
        prediction=pred,
        churn_probability=prob,
        feature_attributions=explanation["all_feature_attributions"],
        top_positive_features=explanation["top_positive_features"],
    )


@app.post("/drift-check", tags=["Monitoring"])
def check_drift(batch: BatchPredictionRequest):
    """Calculates feature and prediction data drift for a incoming inference batch."""
    if MODEL_STATE["drift_detector"] is None:
        load_artifacts()

    df_batch = pd.DataFrame([c.model_dump() for c in batch.customers])
    drift_result = MODEL_STATE["drift_detector"].detect_feature_drift(df_batch)

    # Update Prometheus Drift Gauge
    DATA_DRIFT_GAUGE.set(drift_result["overall_drift_ratio"])

    return drift_result


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus metrics scraper endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
