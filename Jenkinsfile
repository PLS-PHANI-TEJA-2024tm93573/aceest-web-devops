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


    }

}
