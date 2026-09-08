pipeline {
    agent any
    stages {
        stage('Checkout branch') { steps { checkout scm } }
        stage('Test') {
            steps { sh 'python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && LOG_DIR=/tmp/anew-ci-logs .venv/bin/python -m pytest tests -q' }
        }
        stage('Web verify') { steps { dir('frontend') { sh 'npm ci && npm test && npm run build && npm audit --audit-level=high' } } }
        stage('Build branch image') {
            steps { sh 'docker build -t nogonz/anew:build-${BUILD_NUMBER} .' }
        }
    }
}
