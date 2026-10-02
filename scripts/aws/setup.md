# AWS Setup Instructions for RAGOps

## 1. Create S3 Bucket Structure
```bash
aws s3 mb s3://ragops-enterprise-knowledge-bucket --region us-east-1
aws s3 api put-object --bucket ragops-enterprise-knowledge-bucket --key raw-documents/
aws s3 api put-object --bucket ragops-enterprise-knowledge-bucket --key processed-data/
aws s3 api put-object --bucket ragops-enterprise-knowledge-bucket --key dvc-artifacts/
aws s3 api put-object --bucket ragops-enterprise-knowledge-bucket --key mlflow-artifacts/
aws s3 api put-object --bucket ragops-enterprise-knowledge-bucket --key evaluation-reports/
```

## 2. DVC S3 Remote Configuration
```bash
dvc remote add -d s3remote s3://ragops-enterprise-knowledge-bucket/dvc-artifacts/
dvc remote modify s3remote region us-east-1
```
