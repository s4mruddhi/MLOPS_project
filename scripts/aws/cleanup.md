# AWS Cost Control Teardown & Resource Cleanup Procedure

As an academic project demonstration, all AWS cloud resources must be terminated immediately after demonstration to avoid charges.

## 1. Delete SageMaker Endpoint & Endpoint Config
```bash
aws sagemaker delete-endpoint --endpoint-name ragops-retrieval-eval-endpoint
aws sagemaker delete-endpoint-config --endpoint-config-name ragops-retrieval-eval-config
```

## 2. Empty & Delete S3 Bucket
```bash
aws s3 rm s3://ragops-enterprise-knowledge-bucket --recursive
aws s3 rb s3://ragops-enterprise-knowledge-bucket --force
```

## 3. Delete CloudWatch Log Groups
```bash
aws logs delete-log-group --log-group-name /aws/ragops/fastapi-service
```
