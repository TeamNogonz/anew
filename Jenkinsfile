pipeline {
    agent any

    environment {
        imagename = "nogonz/anew"
        registryCredential = 'nogonz-dockerhub'
        envFileCredential = 'ANEW_ENV_FILE'
        dockerImage = ''
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Git Clone') {
            steps {
                git url: 'https://github.com/TeamNogonz/anew.git',
                branch: 'main',
                credentialsId: 'githubJenkins'
            }
            post {
                success { 
                    echo 'Successfully Cloned Repository'
                }
                failure {
                    error 'ERROR ----- [[Cloning Repository]] -----'
                }
            }
        }

        stage('Environment Setup') {
            steps {
                echo 'ECHO ----- [[Environment Setup]] -----'
                script {
                    // Jenkins Credentials에서 .env 파일 내용을 가져와서 생성
                    withCredentials([file(credentialsId: envFileCredential, variable: 'ENV_FILE_CONTENT')]) {
                        writeFile file: '.env', text: ENV_FILE_CONTENT
                        echo 'Successfully created .env file from Jenkins credentials'
                    }
                }
            }
            post {
                failure {
                    error 'ERROR ----- [[Environment Setup Failed]] -----'
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo 'ECHO ----- [[Build Docker]] -----'
                script {
                    // BuildKit 활성화로 멀티스테이지 빌드 최적화
                    sh 'docker build --no-cache -t ${imagename}:latest .'
                    dockerImage = docker.image("${imagename}:latest")
                }
            }
            post {
                failure {
                    error 'ERROR ----- [[Build Docker]] -----'
                }
            }
        }

        stage('Push Docker') {
            steps {
                echo 'ECHO ----- [[Push Docker]] -----'
                script {
                    // latest 태그와 버전 태그 모두 푸시
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push("latest")
                        dockerImage.push("1.0")
                    }
                }
            }
            post {
                failure {
                    error 'ERROR ----- [[Push Docker]] -----'
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'ECHO ----- [[Deploy Application]] -----'
                script {
                    // 기존 컨테이너 정리
                    sh '''
                        docker stop anew-server || true
                        docker rm anew-server || true
                    '''
                    
                    // 새 컨테이너 실행 (환경변수 파일 및 로그 디렉토리 마운트)
                    sh '''
                        docker pull ${imagename}:latest
                        docker run -d \
                            --name anew-server \
                            -p 8000:8000 \
                            --env-file ${WORKSPACE}/.env \
                            -v ${WORKSPACE}/logs:/app/logs \
                            ${imagename}:latest
                            --network nogonz-network
                    '''
                    
                    // 컨테이너 상태 확인
                    sh '''
                        echo "Waiting for container to start..."
                        sleep 10
                        docker ps | grep anew-server
                        docker logs anew-server --tail 20
                    '''
                }
            }
            post {
                failure {
                    error 'ERROR ----- [[Deploy Application]] -----'
                }
                always {
                    // 불필요한 이미지 정리
                    sh 'docker image prune -af'
                }
            }
        }
    }

    post {
        always {
            echo 'ECHO ----- [[Pipeline Completed]] -----'
            cleanWs()
        }
    }
}