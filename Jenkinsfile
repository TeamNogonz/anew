pipeline {
    agent any
    stages {
        stage('Checkout branch') { steps { checkout scm } }
        stage('Test') {
            steps { sh 'python3 -m venv .venv && .venv/bin/pip install -r app/requirements.txt pytest httpx && .venv/bin/python -m pytest tests -q' }
        }
        stage('Build branch image') {
            steps { sh 'docker build -t nogonz/anew:build-${BUILD_NUMBER} .' }
        }
    }
}
