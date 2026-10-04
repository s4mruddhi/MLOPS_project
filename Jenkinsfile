pipeline {
    agent any

    environment {
        USE_TF = '0'
        USE_TORCH = '1'
        PYTHONUNBUFFERED = '1'
        MLFLOW_TRACKING_URI = 'sqlite:///mlflow.db'
    }

    stages {
        stage('Checkout & Environment Setup') {
            steps {
                echo 'Checking out RAGOps Pipeline Repository...'

                checkout scm

                sh 'pwd'
                sh 'ls -la'

                sh 'python3 -m pip install --upgrade pip --break-system-packages || true'
                sh 'pip3 install --break-system-packages -r requirements.txt || pip install --break-system-packages -r requirements.txt || true'
            }
        }

        stage('Phase 4: Document Validation & Chunking') {
            steps {
                sh 'python3 scripts/run_phase4_pipeline.py'
            }
        }

        stage('Phase 5 & 7: Vector Indexing & Retrieval Evaluation') {
            steps {
                sh 'python3 scripts/run_phase5_pipeline.py'
                sh 'python3 scripts/run_phase7_evaluation.py'
            }
        }

        stage('Phase 8 & 10: MLflow Tracking & RAG Evaluation') {
            steps {
                sh 'python3 scripts/run_phase8_mlflow.py'
                sh 'python3 scripts/run_phase10_evaluation.py'
            }
        }

        stage('Phase 11: Airflow DAG Pipeline Execution') {
            steps {
                sh 'python3 scripts/run_phase11_pipeline.py'
            }
        }

        stage('Phase 12, 14 & 15: REST API, Monitoring & Drift Audits') {
            steps {
                sh 'python3 scripts/run_phase12_pipeline.py'
                sh 'python3 scripts/run_phase14_monitoring.py'
                sh 'python3 scripts/run_phase15_drift.py'
            }
        }

        stage('Run Pytest Integration Suite') {
            steps {
                sh 'python3 -m pytest tests/ -v'
            }
        }

        stage('Phase 13: Docker Image Build') {
            steps {
                sh 'docker build -t ragops-assistant-api:latest .'
            }
        }
    }

    post {
        always {
            echo '=================================================='
            echo 'RAGOps Enterprise Jenkins CI/CD Pipeline Completed'
            echo '=================================================='
        }
        success {
            echo 'Pipeline Build & Validation PASSED.'
        }
    }
}
