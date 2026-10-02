# Data Card: Enterprise Customer Churn Dataset

## 1. Dataset Overview
- **Dataset Name**: Enterprise Customer Churn Dataset (`data/raw/customer_churn.csv`)
- **Version**: Version 1.0 (Managed with DVC)
- **Domain**: Telecom / SaaS Subscription Services
- **Size**: 2,500 Customer Records, 10 Attributes

## 2. Dataset Schema & Descriptions
| Feature Name | Data Type | Domain / Range | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | String | `CUST-1000` to `CUST-3499` | Unique Customer Identifier |
| `age` | Integer | [18, 75] | Customer Age in Years |
| `gender` | Categorical | `Male`, `Female` | Self-reported Demographic Gender |
| `tenure` | Integer | [1, 72] | Account Tenure in Months |
| `monthly_charges` | Float | [$20.00, $120.00] | Monthly Recurring Billing Amount |
| `total_charges` | Float | [$20.00, $8640.00] | Lifetime Cumulative Billing Amount |
| `contract` | Categorical | `Month-to-month`, `One year`, `Two year` | Active Subscription Plan Type |
| `payment_method` | Categorical | `Electronic check`, `Mailed check`, `Bank transfer`, `Credit card` | Default Billing Payment Method |
| `support_tickets` | Integer | [0, 8] | Number of Customer Support Tickets Filed |
| `churn` (Target) | Binary | `0` (Retained), `1` (Churned) | Historical Churn Status |

## 3. Data Integrity & Validation Rules
- **Missing Value Handling**: Zero null tolerance across all mandatory fields (`DataValidator`).
- **Domain Constraints**: Range checks on `age` (18-120), `tenure` (0-120), and positive `monthly_charges`.
- **Target Distribution**: ~28.4% Churn Positive Rate (Stratified split enforced during train/test partitioning).

## 4. Anonymization & Privacy (PII)
- PII elements (Names, Social Security Numbers, Credit Card Numbers) are excluded.
- Customer IDs are synthetic hashes (`CUST-XXXX`).

## 5. DVC Data Lineage
- Raw data tracked via `.dvc` pointers pointing to local/S3 remote storage (`../dvc_storage`).
- Reproducible hashing verified via MD5 checksums.
