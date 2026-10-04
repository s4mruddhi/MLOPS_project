"""
Phase 17 Integration Tests: CI/CD Automation & Workflow Validation.
"""

import os
import sys
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


def test_github_actions_workflow_exists_and_valid():
    gh_path = os.path.join(PROJECT_ROOT, ".github", "workflows", "ci_cd.yml")
    assert os.path.exists(gh_path), ".github/workflows/ci_cd.yml must exist"

    with open(gh_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "name" in data
    assert "on" in data or True in data
    assert "jobs" in data
    assert "test_and_evaluate" in data["jobs"]


def test_jenkinsfile_exists_and_valid():
    jenkins_path = os.path.join(PROJECT_ROOT, "Jenkinsfile")
    assert os.path.exists(jenkins_path), "Jenkinsfile must exist"

    with open(jenkins_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "pipeline {" in content
    assert "stages {" in content
    assert "pytest" in content
    assert "docker" in content
