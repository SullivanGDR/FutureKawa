pipeline {
    agent any

    environment {
        BUILD_TAG = "${env.BUILD_NUMBER ?: 'local'}"
        BACKEND_IMAGE = "futurekawa-backend"
        FRONTEND_IMAGE = "futurekawa-frontend"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Build #${BUILD_TAG} — branche: ${env.BRANCH_NAME ?: 'N/A'}"
            }
        }

        stage('Build') {
            steps {
                echo 'Construction des images Docker...'
                sh 'docker compose build --no-cache'
            }
        }

        stage('Test') {
            steps {
                echo 'Tests unitaires backend...'
                sh '''
                    docker run --rm \
                        -e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \
                        futurekawa-backend:latest \
                        sh -c "pip install --quiet pytest && pytest tests/ -v --tb=short"
                '''
            }
        }

        stage('Quality') {
            steps {
                echo 'Qualité du code (flake8)...'
                sh '''
                    docker run --rm \
                        -e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \
                        futurekawa-backend:latest \
                        sh -c "pip install --quiet flake8 && flake8 app/ main.py --max-line-length=120 --count --statistics"
                '''
            }
        }

        stage('Package') {
            steps {
                echo "Tag des images — build #${BUILD_TAG}"
                sh "docker tag ${BACKEND_IMAGE}:latest ${BACKEND_IMAGE}:${BUILD_TAG}"
                sh "docker tag ${FRONTEND_IMAGE}:latest ${FRONTEND_IMAGE}:${BUILD_TAG}"
                sh "docker images | grep futurekawa"
            }
        }
    }

    post {
        success {
            echo "Pipeline reussi — build #${BUILD_TAG}"
        }
        failure {
            echo "Pipeline echoue — build #${BUILD_TAG}"
        }
        always {
            sh 'docker compose down --remove-orphans || true'
            sh 'docker system prune -f --filter label=com.docker.compose.project=futurekawa || true'
        }
    }
}
