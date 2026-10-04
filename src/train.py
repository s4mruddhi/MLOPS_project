"""
Assignment No. 2: Track Machine Learning Experiments Using MLflow
Course: MLOps
Topic: Track Machine Learning Experiments Using MLflow

Steps:
1. Load dataset (data/iris.csv)
2. Perform preprocessing (missing values check, feature scaling, encoding)
3. Split data (80% Train, 20% Test)
4. Train 3 Models: Logistic Regression, Decision Tree, Random Forest
5. Track experiments in MLflow: Log Params, Metrics, Artifacts, Models
6. Compare experiments and select best model
7. Register champion model in MLflow Model Registry
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import mlflow
import mlflow.sklearn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "iris.csv")
ARTIFACTS_TEMP_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "assignment2_artifacts")
os.makedirs(ARTIFACTS_TEMP_DIR, exist_ok=True)

# Set MLflow Tracking URI to SQLite DB for local persistence
MLFLOW_DB_PATH = f"sqlite:///{os.path.join(PROJECT_ROOT, 'mlflow.db')}"
mlflow.set_tracking_uri(MLFLOW_DB_PATH)

EXPERIMENT_NAME = "MLOps_Assignment2_Iris_Tracking"
mlflow.set_experiment(EXPERIMENT_NAME)

def load_and_preprocess_data():
    """Step 1 - Step 3: Load, preprocess, scale, and split dataset"""
    print("--> Step 1: Loading dataset from", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    print("--> Step 2: Preprocessing dataset...")
    # Check missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        df = df.fillna(df.median())

    X = df.drop(columns=["species"])
    y = df["species"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    print("--> Step 3: Splitting dataset (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, list(le.classes_)


def plot_and_save_confusion_matrix(y_true, y_pred, labels, filename):
    """Generate and save confusion matrix heatmap artifact"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()

    file_path = os.path.join(ARTIFACTS_TEMP_DIR, filename)
    plt.savefig(file_path)
    plt.close()
    return file_path


def save_classification_report(y_true, y_pred, labels, filename):
    """Generate and save classification report artifact"""
    report_str = classification_report(y_true, y_pred, target_names=[str(l) for l in labels])
    file_path = os.path.join(ARTIFACTS_TEMP_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_str)
    return file_path


def train_and_track_models():
    """Step 4 - Step 5: Train 3 models and log runs in MLflow"""
    X_train, X_test, y_train, y_test, label_names = load_and_preprocess_data()

    models = [
        {
            "name": "Logistic Regression",
            "model": LogisticRegression(C=1.0, max_iter=200, random_state=42),
            "params": {"model_type": "LogisticRegression", "C": 1.0, "max_iter": 200, "solver": "lbfgs"}
        },
        {
            "name": "Decision Tree",
            "model": DecisionTreeClassifier(max_depth=4, criterion="gini", random_state=42),
            "params": {"model_type": "DecisionTreeClassifier", "max_depth": 4, "criterion": "gini"}
        },
        {
            "name": "Random Forest",
            "model": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            "params": {"model_type": "RandomForestClassifier", "n_estimators": 100, "max_depth": 5}
        }
    ]

    experiment_results = []

    print("\n--> Step 4 & 5: Training models & logging to MLflow...")

    for item in models:
        model_name = item["name"]
        model = item["model"]
        params = item["params"]

        with mlflow.start_run(run_name=model_name) as run:
            run_id = run.info.run_id
            print(f"\n[Run: {model_name}] (Run ID: {run_id})")

            # Train model
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Calculate evaluation metrics
            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, average="macro"))
            rec = float(recall_score(y_test, y_pred, average="macro"))
            f1 = float(f1_score(y_test, y_pred, average="macro"))

            # Log Parameters & Metrics to MLflow
            mlflow.log_params(params)
            mlflow.log_metrics({
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1
            })

            # Save & Log Artifacts (Confusion Matrix & Classification Report)
            cm_filename = f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
            cr_filename = f"classification_report_{model_name.lower().replace(' ', '_')}.txt"

            cm_path = plot_and_save_confusion_matrix(y_test, y_pred, label_names, cm_filename)
            cr_path = save_classification_report(y_test, y_pred, label_names, cr_filename)

            mlflow.log_artifact(cm_path, artifact_path="evaluation_plots")
            mlflow.log_artifact(cr_path, artifact_path="evaluation_reports")

            # Log Model Artifact
            mlflow.sklearn.log_model(model, artifact_path="model")

            print(f"  Accuracy  : {acc:.4f}")
            print(f"  Precision : {prec:.4f}")
            print(f"  Recall    : {rec:.4f}")
            print(f"  F1 Score  : {f1:.4f}")

            experiment_results.append({
                "name": model_name,
                "run_id": run_id,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "model_uri": f"runs:/{run_id}/model"
            })

    # Step 6 & 7: Compare & Select Best Model
    print("\n--> Step 6 & 7: Comparing experiment results...")
    results_df = pd.DataFrame(experiment_results).sort_values(by="f1_score", ascending=False)
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPARISON SUMMARY")
    print("=" * 80)
    print(results_df[["name", "accuracy", "precision", "recall", "f1_score"]].to_string(index=False))
    print("=" * 80)

    best_run = results_df.iloc[0]
    print(f"\n---> BEST PERFORMING MODEL: '{best_run['name']}' (F1 Score: {best_run['f1_score']:.4f})")

    # Step 8: Register Best Model in MLflow Model Registry
    print("\n--> Step 8: Registering best model in MLflow Model Registry...")
    model_name_registry = "Champion_Iris_Classifier"
    registered_model = mlflow.register_model(
        model_uri=best_run["model_uri"],
        name=model_name_registry
    )

    print(f"SUCCESS: Registered Model '{registered_model.name}' Version {registered_model.version} in MLflow Model Registry.")

    return results_df, registered_model

if __name__ == "__main__":
    train_and_track_models()
