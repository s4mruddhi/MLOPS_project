"""
Phase 13 Integration Tests: Docker Containerization & Docker Compose Validation.
"""

import os
import sys
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


def test_dockerfile_exists_and_valid():
    dockerfile_path = os.path.join(PROJECT_ROOT, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile must exist"
    
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "FROM python:3.11-slim" in content
    assert "WORKDIR /app" in content
    assert "EXPOSE 8000" in content
    assert "HEALTHCHECK" in content
    assert "uvicorn" in content
    assert "app.main:app" in content


def test_dockerignore_exists_and_valid():
    dockerignore_path = os.path.join(PROJECT_ROOT, ".dockerignore")
    assert os.path.exists(dockerignore_path), ".dockerignore must exist"

    with open(dockerignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".git" in content
    assert "__pycache__" in content
    assert ".venv" in content or "venv" in content


def test_docker_compose_exists_and_valid():
    compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml must exist"

    with open(compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "services" in data
    services = data["services"]
    
    assert "ragops-api" in services
    assert "airflow" in services
    assert "prometheus" in services
    assert "grafana" in services

    # Validate ports
    assert "8000:8000" in services["ragops-api"]["ports"]
    assert "8080:8080" in services["airflow"]["ports"]
    assert "9090:9090" in services["prometheus"]["ports"]
    assert "3000:3000" in services["grafana"]["ports"]

    # Validate healthcheck
    assert "healthcheck" in services["ragops-api"]


def test_prometheus_config_valid():
    prom_path = os.path.join(PROJECT_ROOT, "prometheus", "prometheus.yml")
    assert os.path.exists(prom_path), "prometheus/prometheus.yml must exist"

    with open(prom_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "scrape_configs" in data
    configs = data["scrape_configs"]
    assert len(configs) > 0
    assert configs[0]["job_name"] == "ragops_fastapi_service"
    assert configs[0]["metrics_path"] == "/metrics"
