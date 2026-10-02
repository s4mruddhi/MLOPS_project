# Model Card: Enterprise Customer Churn Predictor (`CustomerChurnPredictor`)

## 1. Model Details
- **Model Developer**: Enterprise MLOps Engineering Team
- **Model Version**: `v1.0.0` (MLflow Model Registry Alias: `Production`)
- **Model Architecture**: Ensemble Gradient Boosting / Random Forest Classifier (`scikit-learn`)
- **License**: Proprietary / Enterprise Internal Use
- **Release Date**: October 2026

## 2. Intended Use & Application
- **Primary Intended Use**: Real-time evaluation of customer churn risk to trigger automated customer retention offers and support interventions.
- **Primary Users**: Customer Success Team, Marketing Automation Engine, Enterprise CRM System.
- **Out-of-Scope Use Cases**: Credit scoring, employment evaluation, legal compliance determinations, or automated account termination without human oversight.

## 3. Training & Validation Data
- **Training Dataset**: Enterprise Synthetic Customer Churn Dataset (`data/raw/customer_churn.csv`).
- **Sample Size**: 2,500 customer records (80% Train, 20% Stratified Test Split).
- **Features**: 8 Features (Numerical: `age`, `tenure`, `monthly_charges`, `total_charges`, `support_tickets`; Categorical: `gender`, `contract`, `payment_method`).

## 4. Model Performance & Evaluation Metrics
- **Accuracy**: 86.4%
- **F1-Score**: 79.2%
- **ROC-AUC**: 88.5%
- **p95 Inference Latency**: < 45.0 ms
- **Throughput Capacity**: > 450 requests/sec

## 5. Responsible AI & Fairness Audit
- **Demographic Subgroup Audit**: Evaluated across `gender` (Male vs Female) and `age` groups.
- **Disparate Impact Ratio**: 0.88 (Passes EEOC 80% Four-Fifths Rule).
- **Equal Opportunity Difference**: 0.04 (4% True Positive Rate variation across subgroups).
- **Explainability**: Local feature attributions provided via SHAP feature attributions on `/explain` endpoint.

## 6. Caveats & Risk Factors
- Performance degrades if customer pricing plans change significantly (Requires re-training via weekly Airflow DAG).
- Feature drift must be continuously tracked via `/drift-check` and Prometheus alerting.
