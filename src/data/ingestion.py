"""
Data Ingestion Module.
Simulates/Fetches enterprise dataset and saves to raw data path.
"""

import os
import numpy as np
import pandas as pd
from src.config import RAW_DATA_PATH, set_seed


def generate_enterprise_churn_dataset(n_samples: int = 2000) -> pd.DataFrame:
    """Generates synthetic enterprise customer churn dataset with demographic & numerical features."""
    set_seed(42)

    customer_ids = [f"CUST-{1000 + i}" for i in range(n_samples)]
    age = np.random.randint(18, 75, size=n_samples)
    gender = np.random.choice(["Male", "Female"], size=n_samples, p=[0.49, 0.51])
    tenure_months = np.random.randint(1, 72, size=n_samples)
    monthly_charges = np.round(np.random.uniform(20.0, 120.0, size=n_samples), 2)
    total_charges = np.round(monthly_charges * tenure_months + np.random.normal(0, 10, size=n_samples), 2)
    total_charges = np.maximum(total_charges, 20.0)

    contract_type = np.random.choice(
        ["Month-to-month", "One year", "Two year"], size=n_samples, p=[0.55, 0.25, 0.20]
    )
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        size=n_samples,
        p=[0.35, 0.25, 0.20, 0.20],
    )
    support_tickets = np.random.poisson(lam=1.5, size=n_samples)

    logit = (
        -0.08 * tenure_months
        + 0.03 * monthly_charges
        + 0.85 * support_tickets
        + np.where(contract_type == "Month-to-month", 1.5, -1.2)
        - 1.0
    )
    prob_churn = 1 / (1 + np.exp(-logit))
    churn = (np.random.uniform(0, 1, size=n_samples) < prob_churn).astype(int)

    df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "age": age,
            "gender": gender,
            "tenure": tenure_months,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "contract": contract_type,
            "payment_method": payment_method,
            "support_tickets": support_tickets,
            "churn": churn,
        }
    )

    return df


def ingest_data(output_path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Ingests dataset and saves to specified raw data location."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_enterprise_churn_dataset(n_samples=2500)
    df.to_csv(output_path, index=False)
    print(f"[Ingestion] Successfully ingested {len(df)} records into '{output_path}'.")
    return df


if __name__ == "__main__":
    ingest_data()
