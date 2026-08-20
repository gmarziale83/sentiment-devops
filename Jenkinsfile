pipeline {
    agent any

    environment {
        // Usa host.docker.internal se Jenkins gira dentro un container Docker, altrimenti localhost
        API_URL = 'http://host.docker.internal:8000'
        NOTIFICATION_EMAIL = 'admin@example.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'python3 -m venv venv || python -m venv venv'
                sh './venv/bin/pip install -r app/requirements.txt || .\\venv\\Scripts\\pip install -r app/requirements.txt'
                sh './venv/bin/pytest tests/test_unit.py -W ignore::DeprecationWarning || .\\venv\\Scripts\\pytest tests/test_unit.py -W ignore::DeprecationWarning'
            }
        }

        stage('Build & Deploy Containers') {
            steps {
                // In ambiente reale/Agent con Docker installato:
                sh 'docker compose down || true'
                sh 'docker compose up --build -d'
            }
        }

        stage('Integration Tests') {
            steps {
                sh './venv/bin/pytest tests/test_integration.py || .\\venv\\Scripts\\pytest tests/test_integration.py'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'SUCCESS: Pipeline completata con successo.'
            mail to: "${env.NOTIFICATION_EMAIL}",
                 subject: "SUCCESS: Pipeline #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                 body: "La pipeline di Sentiment Analysis ha superato i test ed eseguito il deploy con successo."
        }
        failure {
            echo 'FAILURE: Errore durante l esecuzione della Pipeline.'
            mail to: "${env.NOTIFICATION_EMAIL}",
                 subject: "FAILURE: Pipeline #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                 body: "Errore durante la build/deploy della pipeline #${env.BUILD_NUMBER}. Verificare i log di Jenkins."
        }
    }
}