pipeline {

    agent any 


    stages {

        stage ('Checkout Code') {

            steps {
                git branch: 'main',
                    url: 'https://github.com/PLS-PHANI-TEJA-2024tm93573/aceest-web-devops.git'
            }

        }
        stage ('Create Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }


        stage ('Lint Check') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 .
                '''
            }
        }

        stage ('Build Validation') {
            steps {
                sh '''
                . venv/bin/activate
                python -m py_compile app/*py
                '''
            }
        }

        stage ('Build and Push Docker Image') {
            steps {
                sh '''
                docker build -t aceest-web-devops:latest .
                docker tag aceest-web-devops:latest plsphaniteja2024tm93573/aceest-web-app-2024tm93573:latest
                docker push plsphaniteja2024tm93573/aceest-web-app-2024tm93573:latest
                '''
            }
        }

        stage ('Build Docker Test Image') {
            steps {
                sh '''
                docker build -t aceest-web-devops-test:latest -f test.Dockerfile .
                '''
            }
        }

        stage ('Run Tests in Docker Container') {
                steps {
                    sh '''
                    docker run --rm aceest-web-devops-test:latest --name aceest-web-devops-test
                    '''
                }
        }


    }

}
