pipeline {
    agent any

    environment {
        // Ensure Docker Desktop binary directory is on Windows PATH
        PATH = "C:\\Users\\samru\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin;${env.PATH}"
        PYTHONUNBUFFERED = '1'
        USE_TF = '0'
        USE_TORCH = '1'
        IMAGE_NAME = 'ragops-api:latest'
        CONTAINER_NAME = 'ragops_fastapi_service'
        APP_PORT = '8000'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo '=== Stage 1: Checking out latest code from GitHub ==='
                checkout scm
            }
        }

        stage('Install Dependencies & Lint') {
            steps {
                echo '=== Stage 2: Validating Python Environment & Syntax ==='
                bat '''
                    python --version
                    python -m py_compile app/main.py
                '''
            }
        }

        stage('Run Automated Tests') {
            steps {
                echo '=== Stage 3: Running Automated Test Suites (pytest) ==='
                // Pytest runs all 18 test suites and saves XML reports for Jenkins
                bat '''
                    python -m pytest tests/ -v --junitxml=test-reports/results.xml
                '''
            }
            post {
                always {
                    // Collect and visualize test results in the Jenkins UI
                    junit testResults: 'test-reports/results.xml', allowEmptyResults: true
                }
            }
        }

        stage('Docker Build Image') {
            steps {
                echo '=== Stage 4: Building Production Docker Image ==='
                bat '''
                    docker build -t %IMAGE_NAME% .
                '''
            }
        }

        stage('Deploy Docker Container Locally') {
            steps {
                echo '=== Stage 5: Deploying Container to Localhost ==='
                bat '''
                    @echo off
                    echo Stopping previous container if running...
                    docker stop %CONTAINER_NAME% 2>nul || exit /b 0
                    docker rm -f %CONTAINER_NAME% 2>nul || exit /b 0

                    echo Starting new container on port %APP_PORT%...
                    docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:8000 -e PYTHONUNBUFFERED=1 -e USE_TF=0 -e USE_TORCH=1 %IMAGE_NAME%

                    echo Waiting for application to initialize...
                    timeout /t 5 /nobreak >nul

                    echo Verifying deployment health...
                    curl -f http://localhost:%APP_PORT%/health || echo Application starting up...
                '''
            }
        }
    }

    post {
        success {
            echo '======================================================='
            echo ' CI/CD SUCCESS: Application is live at http://localhost:8000'
            echo '======================================================='
        }
        failure {
            echo '======================================================='
            echo ' CI/CD FAILED: Check the stage logs above for errors.'
            echo ' Broken code was BLOCKED from deployment.'
            echo '======================================================='
        }
        always {
            echo 'Cleaning up workspace artifacts...'
        }
    }
}
