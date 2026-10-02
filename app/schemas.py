"""
FastAPI Request & Response Data Validation Schemas (Pydantic v2).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class CustomerInputSchema(BaseModel):
    customer_id: str = Field(..., example="CUST-1001", description="Unique customer identifier")
    age: int = Field(..., ge=18, le=120, example=35, description="Customer age (18-120)")
    gender: str = Field(..., example="Female", description="Gender ('Male' or 'Female')")
    tenure: int = Field(..., ge=0, le=120, example=24, description="Tenure in months")
    monthly_charges: float = Field(..., gt=0.0, example=65.50, description="Monthly charges amount")
    total_charges: float = Field(..., gt=0.0, example=1572.00, description="Total lifetime charges")
    contract: str = Field(..., example="One year", description="Contract type ('Month-to-month', 'One year', 'Two year')")
    payment_method: str = Field(..., example="Credit card", description="Payment method")
    support_tickets: int = Field(..., ge=0, example=1, description="Number of support tickets filed")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ["Male", "Female"]:
            raise ValueError("gender must be 'Male' or 'Female'")
        return v

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v: str) -> str:
        allowed = ["Month-to-month", "One year", "Two year"]
        if v not in allowed:
            raise ValueError(f"contract must be one of {allowed}")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment(cls, v: str) -> str:
        allowed = ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
        if v not in allowed:
            raise ValueError(f"payment_method must be one of {allowed}")
        return v


class BatchPredictionRequest(BaseModel):
    customers: List[CustomerInputSchema]


class SinglePredictionResponse(BaseModel):
    customer_id: str
    prediction: int = Field(..., description="0 for Retain, 1 for Churn")
    churn_probability: float = Field(..., description="Probability of customer churn (0.0 to 1.0)")
    risk_level: str = Field(..., description="'LOW', 'MEDIUM', or 'HIGH'")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")
    model_version: str


class ExplanationResponse(BaseModel):
    customer_id: str
    prediction: int
    churn_probability: float
    feature_attributions: Dict[str, float]
    top_positive_features: Dict[str, float]


class HealthCheckResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    version: str
