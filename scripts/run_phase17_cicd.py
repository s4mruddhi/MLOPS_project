"""
Phase 17 Verification Script: CI/CD Automation & Workflow Validation.
"""

import os
import sys
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


def main():
    print("==================================================")
    print("PHASE 17 — CI/CD AUTOMATION & WORKFLOW PIPELINE")
    print("==================================================")

    # 1. GitHub Actions Workflow Validation
    print("\n[Step 1] Inspecting GitHub Actions Workflow (.github/workflows/ci_cd.yml)...")
    gh_workflow_path = os.path.join(PROJECT_ROOT, ".github", "workflows", "ci_cd.yml")
    assert os.path.exists(gh_workflow_path), "GitHub Actions workflow missing"

    with open(gh_workflow_path, "r", encoding="utf-8") as f:
        gh_data = yaml.safe_load(f)

    print(f"Workflow Name: '{gh_data.get('name')}'")
    print(f"Triggers: {list(gh_data.get('on', {}).keys())}")
    jobs = list(gh_data.get("jobs", {}).keys())
    print(f"Configured Jobs: {jobs}")
    assert "test_and_evaluate" in jobs

    steps = [s.get("name") for s in gh_data["jobs"]["test_and_evaluate"]["steps"] if "name" in s]
    print(f"Workflow Step Count ({len(steps)}): {steps[:5]}...")

    # 2. Jenkinsfile Pipeline Validation
    print("\n[Step 2] Inspecting Jenkinsfile Configuration...")
    jenkinsfile_path = os.path.join(PROJECT_ROOT, "Jenkinsfile")
    assert os.path.exists(jenkinsfile_path), "Jenkinsfile missing"

    with open(jenkinsfile_path, "r", encoding="utf-8") as f:
        jenkins_content = f.read()

    assert "pipeline {" in jenkins_content
    assert "stage('Phase 4: Document Validation & Chunking')" in jenkins_content
    assert "stage('Phase 13: Docker Image Build')" in jenkins_content
    print("Jenkinsfile pipeline syntax and stages successfully verified.")

    print("\n==================================================")
    print("PHASE 17 CI/CD WORKFLOW PIPELINE VERIFIED SUCCESSFUL!")
    print("==================================================")


if __name__ == "__main__":
    main()
