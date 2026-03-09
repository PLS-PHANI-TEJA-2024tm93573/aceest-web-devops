pipeline {

    agent any

    environment {
        IMAGE_NAME = "plsphaniteja2024tm93573/aceest-web-app-2024tm93573"
    }

    stages {

        stage('Checkout Repository') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Latest Tag') {
            steps {
                script {
                    env.LATEST_TAG = sh(
                        script: "git describe --tags \$(git rev-list --tags --max-count=1)",
                        returnStdout: true
                    ).trim()

                    echo "Latest tag detected: ${env.LATEST_TAG}"

                    sh "git checkout ${env.LATEST_TAG}"
                }
            }
        }

        stage('Create Python Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Lint Check') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 .
                '''
            }
        }

        stage('Build Validation') {
            steps {
                sh '''
                . venv/bin/activate
                python -m py_compile app/*.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t aceest-web-devops:latest .
                '''
            }
        }

        stage('Build Docker Test Image') {
            steps {
                sh '''
                docker build -t aceest-web-devops-test:latest -f test.Dockerfile .
                '''
            }
        }

        stage('Run Tests in Docker Container') {
            steps {
                sh '''
                docker run --rm aceest-web-devops-test:latest
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                echo "Pushing Docker image with tag: $LATEST_TAG"

                docker tag aceest-web-devops:latest $IMAGE_NAME:$LATEST_TAG
                docker push $IMAGE_NAME:$LATEST_TAG
                '''
            }
        }

    }
}
