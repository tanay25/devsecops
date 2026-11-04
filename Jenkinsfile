pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'tanay25/flask-devsecops'
        CONTAINER_NAME = 'flask-devsecops-app'
    }

    stages {

        stage('1. Checkout') {
            steps {
                checkout scm
            }
        }

        stage('2. Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('3. Unit Testing') {
            steps {
                sh '''
                    .venv/bin/pytest -v
                '''
            }
        }

        stage('4. Bandit Security Scan') {
            steps {
                sh '''
		    .venv/bin/bandit -r . -x .venv,venv,tests,build,dist -ll -f json -o bandit-report.json || true

                   '''
            }
        }


        stage('5. Dependency Audit') {
            steps {
                sh '''
                    .venv/bin/pip-audit \
                      -f json \
                      -o pip-audit-report.json
                '''
            }
        }

        stage('6. SonarQube Analysis') {
    steps {
        script {
            def scannerHome = tool 'SonarScanner'

            withSonarQubeEnv('sonarqube') {
                sh """
                    ${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=flask-login-app \
                    -Dsonar.projectName=Flask-Login-App \
                    -Dsonar.sources=. \
                    -Dsonar.python.version=3.12 \
                    -Dsonar.exclusions=.venv/**,venv/**,**/__pycache__/**
                """
            }
        }
    }
}

        stage('7. Sonar Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        def qualityGate = waitForQualityGate()
                        if (qualityGate.status != 'OK') {
                            error "SonarQube Quality Gate Failed"
                        }
                    }
                }
            }
        }

        stage('8. Docker Build') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('9. Trivy Image Scan') {
            steps {
                sh '''
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --exit-code 1 \
                      ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('10. Docker Hub Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DOCKER_PASS" | docker login \
                          -u "$DOCKER_USER" --password-stdin

                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${IMAGE_NAME}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('11. Deploy Flask Application') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --restart unless-stopped \
                      -p 5000:5000 \
                      ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }


	stage('12. Health Check') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost:5000/health; then
                            echo "Application is healthy"
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "Application health check failed"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts:
                '*-report.json',
                allowEmptyArchive: true

            echo 'Jenkins pipeline completed.'
        }

        success {
            echo 'DevSecOps pipeline SUCCESS'
        }

        failure {
            echo 'DevSecOps pipeline FAILED'
        }
    }
}
