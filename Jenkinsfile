pipeline {
    agent any

    environment {
        imagename = "nogonz/anew"
        registryCredential = 'nogonz-dockerhub'
        dockerImage = ''
    }

    stages {
        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/TeamNogonz/Bdam-server.git',
                branch: 'main',
                credentialsId: 'githubJenkins'
            }
            post {
                success { 
                    echo 'Successfully Cloned Repository'
                }
                failure {
                    error 'ERROR ----- [[Clonning Repository]] -----'
                }
            }
        }

        stage('Bulid Docker') {
          agent any
          steps {
            echo 'ECHO ----- [[Bulid Docker]] -----'
                dir ('/var/jenkins_home/workspace/anew-server'){
                    script {
                        dockerImage = docker.build imagename
                    }
                }
          }
          post {
            failure {
              error 'ERROR ----- [[Bulid Docker]] -----'
            }
          }
        }

        stage('Push Docker') {
          agent any
          steps {
            echo 'ECHO ----- [[Push Docker]] -----'
            script {
                dir("${env.WORKSPACE}") {
                    // first param '' is default registry (Docker Hub)
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push("1.0")
                    }
                }   
            }
          }
          post {
            failure {
              error 'ERROR ----- [[Push Docker]] -----'
            }
          }
        }

        stage('Docker Run') {
            steps {
                echo 'ECHO ----- [[Pull Docker Image & Docker Image Run]] -----'
                    sh """
                        docker pull nogonz/anew:1.0
                        docker stop anew-server && docker rm anew-server | true
                        docker run -d -p 8000:8000 -v /nogonz/anew/app:/app --name anew-server -u root nogonz/anew:1.0
                        docker image prune -af
                    """ 
                echo 'ECHO ----- [[Pull Docker Image & Docker Image Run DONE]] -----'
            }
        }
    }
}