pipeline {
    agent any
    
    environment {
        // Azure Container Registry credentials
        ACR_REGISTRY = 'agenticaidevacr45141.azurecr.io'
        ACR_CREDENTIALS_ID = '3c81530c-191f-4310-b866-ec6a6abc9e3f' // Jenkins credential ID for ACR
        
        // Image details
        IMAGE_NAME = 'db-agent'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        FULL_IMAGE_NAME = "${ACR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE_NAME = "${ACR_REGISTRY}/${IMAGE_NAME}:latest"
        
        // Git commit info
        GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
                sh 'git rev-parse --short HEAD > .git/commit-id'
            }
        }
        
        stage('Build Info') {
            steps {
                script {
                    echo "Building image: ${FULL_IMAGE_NAME}"
                    echo "Git commit: ${GIT_COMMIT_SHORT}"
                    echo "Build number: ${env.BUILD_NUMBER}"
                }
            }
        }
        
        stage('Lint & Test') {
            steps {
                echo 'Running linting and tests...'
                script {
                    // Install dependencies and run tests
                    sh '''
                        python3 --version
                        pip3 install --user -e .
                        # Add your test commands here
                        # pip3 install --user pytest
                        # pytest tests/ || true
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    sh """
                        docker build -t ${FULL_IMAGE_NAME} .
                        docker tag ${FULL_IMAGE_NAME} ${LATEST_IMAGE_NAME}
                    """
                }
            }
        }
        
        stage('Push to ACR') {
            steps {
                echo 'Pushing Docker image to Azure Container Registry...'
                script {
                    withCredentials([usernamePassword(
                        credentialsId: "${ACR_CREDENTIALS_ID}",
                        usernameVariable: 'ACR_USERNAME',
                        passwordVariable: 'ACR_PASSWORD'
                    )]) {
                        sh """
                            echo ${ACR_PASSWORD} | docker login ${ACR_REGISTRY} -u ${ACR_USERNAME} --password-stdin
                            docker push ${FULL_IMAGE_NAME}
                            docker push ${LATEST_IMAGE_NAME}
                            docker logout ${ACR_REGISTRY}
                        """
                    }
                }
            }
        }
        
        stage('Update Deployment Manifest') {
            steps {
                echo 'Updating deployment manifest...'
                script {
                    // This step will update your ArgoCD manifest repo with the new image tag
                    // You'll need to configure this based on your ArgoCD manifest repo structure
                    sh """
                        echo "Image ${FULL_IMAGE_NAME} is ready for deployment"
                        echo "Update your ArgoCD manifest with this image tag: ${IMAGE_TAG}"
                    """
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                echo 'Cleaning up local Docker images...'
                script {
                    sh """
                        docker rmi ${FULL_IMAGE_NAME} || true
                        docker rmi ${LATEST_IMAGE_NAME} || true
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Image: ${FULL_IMAGE_NAME}"
        }
        failure {
            echo "Pipeline failed. Please check the logs."
        }
        always {
            cleanWs()
        }
    }
}
