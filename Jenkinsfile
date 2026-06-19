pipeline {
    agent any

    environment {
        BUILD_TAG      = "${env.BUILD_NUMBER ?: 'local'}"
        BACKEND_IMAGE  = 'futurekawa-backend'
        FRONTEND_IMAGE = 'futurekawa-frontend'
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
                sh 'docker compose build'
            }
        }

        stage('Tests — Backend') {
            steps {
                sh """
                    TEST_FAILED=false
                    docker run --name test-backend-${BUILD_TAG} \\
                        -e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \\
                        ${BACKEND_IMAGE}:latest \\
                        sh -c "pip install --quiet pytest && mkdir -p /results && pytest tests/ -v --tb=short --junitxml=/results/backend-junit.xml" \\
                        || TEST_FAILED=true

                    mkdir -p test-results
                    docker cp test-backend-${BUILD_TAG}:/results/backend-junit.xml test-results/backend-junit.xml || true
                    docker rm test-backend-${BUILD_TAG} || true

                    if [ "\$TEST_FAILED" = "true" ]; then exit 1; fi
                """
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results/backend-junit.xml'
                }
            }
        }

        stage('Tests — Frontend') {
            steps {
                sh """
                    TEST_FAILED=false
                    docker run --name test-frontend-${BUILD_TAG} \\
                        ${FRONTEND_IMAGE}:latest \\
                        sh -c "mkdir -p /app/test-results && npm run test:ci" \\
                        || TEST_FAILED=true

                    docker cp test-frontend-${BUILD_TAG}:/app/test-results/frontend-junit.xml test-results/frontend-junit.xml || true
                    docker rm test-frontend-${BUILD_TAG} || true

                    if [ "\$TEST_FAILED" = "true" ]; then exit 1; fi
                """
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results/frontend-junit.xml'
                }
            }
        }

        stage('Qualité — flake8') {
            steps {
                sh """
                    docker run --rm \\
                        -e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \\
                        ${BACKEND_IMAGE}:latest \\
                        sh -c "pip install --quiet flake8 && flake8 app/ main.py --max-line-length=120 --count --statistics"
                """
            }
        }

        stage('Package') {
            steps {
                sh "docker tag ${BACKEND_IMAGE}:latest  ${BACKEND_IMAGE}:${BUILD_TAG}"
                sh "docker tag ${FRONTEND_IMAGE}:latest ${FRONTEND_IMAGE}:${BUILD_TAG}"
                sh "docker images | grep futurekawa"
            }
        }
    }

    post {
        success {
            echo "Pipeline reussi — build #${BUILD_TAG}"
            archiveArtifacts artifacts: 'test-results/*.xml', allowEmptyArchive: true
        }
        failure {
            echo "Pipeline echoue — build #${BUILD_TAG}"
        }
        always {
            // Nettoyage des conteneurs de test uniquement — PAS docker compose down (tuerait Jenkins)
            sh "docker rm test-backend-${BUILD_TAG} test-frontend-${BUILD_TAG} 2>/dev/null || true"
        }
    }
}
