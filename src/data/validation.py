"""
Data Quality & Schema Validation Module.
Checks data integrity, missing values, range constraints, and domain values.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd


class DataValidator:
    """Validates data schema and quality constraints for raw datasets."""

    EXPECTED_COLUMNS = [
        "customer_id",
        "age",
        "gender",
        "tenure",
        "monthly_charges",
        "total_charges",
        "contract",
        "payment_method",
        "support_tickets",
        "churn",
    ]

    ALLOWED_GENDERS = {"Male", "Female"}
    ALLOWED_CONTRACTS = {"Month-to-month", "One year", "Two year"}
    ALLOWED_PAYMENTS = {"Electronic check", "Mailed check", "Bank transfer", "Credit card"}

    @classmethod
    def validate(cls, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Missing Column Check
        missing_cols = set(cls.EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        if errors:
            return False, errors

        # 2. Null / Missing Value Check
        null_counts = df[cls.EXPECTED_COLUMNS].isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]
        if not cols_with_nulls.empty:
            errors.append(f"Found unexpected missing values: {cols_with_nulls.to_dict()}")

        # 3. Numeric Range Validation
        if (df["age"] < 18).any() or (df["age"] > 120).any():
            errors.append("Invalid age values found (must be between 18 and 120)")

        if (df["tenure"] < 0).any() or (df["tenure"] > 120).any():
            errors.append("Invalid tenure values found (must be between 0 and 120)")

        if (df["monthly_charges"] <= 0).any():
            errors.append("Invalid monthly_charges found (must be positive)")

        # 4. Categorical Domain Validation
        invalid_genders = set(df["gender"].unique()) - cls.ALLOWED_GENDERS
        if invalid_genders:
            errors.append(f"Invalid gender values: {invalid_genders}")

        invalid_contracts = set(df["contract"].unique()) - cls.ALLOWED_CONTRACTS
        if invalid_contracts:
            errors.append(f"Invalid contract values: {invalid_contracts}")

        invalid_payments = set(df["payment_method"].unique()) - cls.ALLOWED_PAYMENTS
        if invalid_payments:
            errors.append(f"Invalid payment method values: {invalid_payments}")

        # 5. Target Label Validation
        target_vals = set(df["churn"].unique())
        if not target_vals.issubset({0, 1}):
            errors.append(f"Target 'churn' must be binary (0 or 1), got {target_vals}")

        is_valid = len(errors) == 0
        return is_valid, errors
