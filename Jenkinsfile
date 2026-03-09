pipeline {

    agent any

    environment {
        IMAGE_NAME = "plsphaniteja2024tm93573/aceest-web-app-2024tm93573"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
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
                echo "Docker image built successfully"
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

        stage('Push Docker Image (Tags Only)') {

            when {
                buildingTag()
            }

            steps {
                sh '''
                echo "Tag detected: $TAG_NAME"

                docker tag aceest-web-devops:latest $IMAGE_NAME:$TAG_NAME
                docker push $IMAGE_NAME:$TAG_NAME
                '''
            }
        }

    }

}