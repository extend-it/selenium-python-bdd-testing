// Pipeline for when the project lives in a Git repository (Pipeline-from-SCM job).
// The local Docker Jenkins uses an equivalent inline job that copies the mounted
// project folder instead of checking out from Git (see jenkins/casc/jenkins.yaml).
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(name: 'MARKERS', choices: ['', 'smoke', 'login', 'cart'], description: 'pytest -m filter (empty = all)')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('UI tests') {
            steps {
                sh '''
                    if [ -n "$MARKERS" ]; then
                        bash scripts/run_tests.sh -m "$MARKERS"
                    else
                        bash scripts/run_tests.sh
                    fi
                '''
            }
        }
    }

    post {
        always {
            allure includeProperties: false, jdk: '', commandline: 'allure', results: [[path: 'allure-results']]
        }
    }
}
