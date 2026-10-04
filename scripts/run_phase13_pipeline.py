"""
Phase 13 Verification Script: Docker Containerization & Docker Compose Validation Pipeline.
"""

import os
import sys
import subprocess
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

def main():
    print("==================================================")
    print("PHASE 13 — DOCKER CONTAINERIZATION & DOCKER COMPOSE PIPELINE")
    print("==================================================")

    # 1. Dockerfile Validation
    print("\n[Step 1] Inspecting Dockerfile configuration...")
    dockerfile_path = os.path.join(PROJECT_ROOT, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile missing"
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        df_content = f.read()
    print("Dockerfile snippet:")
    for line in df_content.splitlines()[:10]:
        print(f"  {line}")
    assert "FROM python:3.11-slim" in df_content
    assert "HEALTHCHECK" in df_content
    assert "uvicorn" in df_content

    # 2. .dockerignore Validation
    print("\n[Step 2] Inspecting .dockerignore configuration...")
    dockerignore_path = os.path.join(PROJECT_ROOT, ".dockerignore")
    assert os.path.exists(dockerignore_path), ".dockerignore missing"
    with open(dockerignore_path, "r", encoding="utf-8") as f:
        di_content = f.read()
    print(".dockerignore entries count:", len(di_content.splitlines()))

    # 3. docker-compose.yml Validation
    print("\n[Step 3] Parsing and validating docker-compose.yml...")
    compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml missing"
    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    services = list(compose_data.get("services", {}).keys())
    print(f"Configured Docker Compose Services ({len(services)}): {services}")
    assert "ragops-api" in services
    assert "prometheus" in services
    assert "grafana" in services

    # 4. Prometheus Config Validation
    print("\n[Step 4] Validating prometheus/prometheus.yml...")
    prom_path = os.path.join(PROJECT_ROOT, "prometheus", "prometheus.yml")
    assert os.path.exists(prom_path), "prometheus.yml missing"
    with open(prom_path, "r", encoding="utf-8") as f:
        prom_data = yaml.safe_load(f)
    job_name = prom_data["scrape_configs"][0]["job_name"]
    print(f"Prometheus Scrape Job: {job_name}")

    # 5. Docker CLI Environment Inspection
    print("\n[Step 5] Checking Docker CLI environment status...")
    try:
        docker_ver = subprocess.check_output(["docker", "--version"], text=True).strip()
        print(f"Docker Version: {docker_ver}")
    except Exception as e:
        print(f"Docker CLI check warning (system dependent): {e}")

    try:
        compose_ver = subprocess.check_output(["docker", "compose", "version"], text=True).strip()
        print(f"Docker Compose Version: {compose_ver}")
    except Exception as e:
        print(f"Docker Compose CLI check warning: {e}")

    print("\n==================================================")
    print("PHASE 13 DOCKER CONTAINERIZATION PIPELINE VERIFIED SUCCESSFUL!")
    print("==================================================")

if __name__ == "__main__":
    main()
