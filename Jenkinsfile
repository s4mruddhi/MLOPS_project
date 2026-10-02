pipeline {
    agent any

    environment {
        PYTHON_ENV = 'venv'
        AWS_REGION = 'us-east-1'
        AWS_S3_BUCKET = 'ragops-enterprise-knowledge-bucket'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/samrudhideshmukh12413724/MLOPS_project.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Document Ingestion & Validation') {
            steps {
                bat 'python src/data/ingestion.py'
                bat 'python -c "from src.data.ingestion import ingest_data; from src.data.validation import DataValidator; DataValidator.validate(ingest_data())"'
            }
        }

        stage('RAG Embedding & Vector Indexing') {
            steps {
                bat 'python -c "import json; from src.data.preprocessing import preprocess_rag_data; docs=json.load(open(\'data/raw/knowledge_docs.json\')); preprocess_rag_data(docs, fit=True)"'
            }
        }

        stage('RAG Candidate Benchmark & MLflow Registration') {
            steps {
                bat 'python src/models/train.py'
            }
        }

        stage('Run Pytest Integration Suite') {
            steps {
                bat 'python -m pytest tests/ -v'
            }
        }

        stage('Docker Image Build') {
            steps {
                bat 'docker build -t ragops-assistant-api:latest .'
            }
        }
    }

    post {
        always {
            echo 'RAGOps Jenkins Pipeline Completed.'
        }
    }
}
