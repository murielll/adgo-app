pipeline {
    agent { docker { 
                image 'python:3.8-alpine' 
                args '-u root:root --env-file ${JENKINS_HOME}/env-files/adgo-app/env'
                
            }
    }

    stages {
        stage('Build') {
            steps {
                echo '------------------Start building------------------'
                sh '''
                   apk add --update --no-cache openldap-dev gcc linux-headers build-base git openssh-client
                   git clone https://github.com/murielll/adgo-app.git 
                   cd adgo-app
                   pip install -r requirements.txt
                '''
                echo '------------------Stop building------------------'
            }
        }

        stage('Lint') {
            steps {
                echo '------------------Start linting------------------'
                sh '''
                    cd adgo-app
                    pylint --errors-only app/*.py
                '''
                echo '------------------Stop linting------------------'
            }
        }

        stage('Test') {
            steps {
                echo '------------------Start testing------------------'
                sh '''
                    cd adgo-app/app
                    pytest --disable-warnings
                '''
                echo '------------------Stop testing------------------'
            }
        }

        stage('Deploy') {
            steps {
                echo '------------------Start deploying------------------'
               sshagent (credentials: ['github-ssh-key']) {
                    sh 'ssh -o StrictHostKeyChecking=no -l adgo ${ADGO_DEV_SERVER_IP}  "docker ps -f name=adgo_app -q > app_cont.txt"'
                    sh 'ssh -o StrictHostKeyChecking=no -l adgo ${ADGO_DEV_SERVER_IP}  "cd adgo-app; git pull; [[ -s ../app_cont.txt ]] && ./restart.sh || ./start.sh "'
                }
               
                echo '------------------Stop deploying------------------'
            }
        }
    }
    
    post { 
        always { 
            cleanWs()
        }
    }
}
