pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: agent
spec:
  serviceAccountName: jenkins-admin
  containers:
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-storage
      mountPath: /var/lib/docker
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
  - name: jnlp
    image: jenkins/inbound-agent:latest-jdk17
    args:
    - \$(JENKINS_SECRET)
    - \$(JENKINS_NAME)
    env:
    - name: DOCKER_HOST
      value: tcp://localhost:2375
  volumes:
  - name: docker-storage
    emptyDir: {}
"""
        }
    }
   
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
       
        stage('Build & Push Docker Image') {
            steps {
                container('docker') {
                    script {
                        // Wait for Docker daemon to be ready
                        sh '''
                            timeout=60
                            while ! docker info >/dev/null 2>&1; do
                                timeout=$((timeout - 1))
                                if [ $timeout -le 0 ]; then
                                    echo "Docker daemon failed to start"
                                    exit 1
                                fi
                                echo "Waiting for Docker daemon to start..."
                                sleep 1
                            done
                            echo "Docker daemon is ready"
                        '''
                       
                        // Build Docker image
                        sh "docker build -t ${FULL_IMAGE_NAME} -t ${LATEST_IMAGE_NAME} ."
                       
                        // Login to ACR and push images
                        withCredentials([usernamePassword(credentialsId: "${ACR_CREDENTIALS_ID}",
                                                         passwordVariable: 'ACR_PASSWORD',
                                                         usernameVariable: 'ACR_USERNAME')]) {
                            sh """
                                echo \$ACR_PASSWORD | docker login ${ACR_REGISTRY} -u \$ACR_USERNAME --password-stdin
                                docker push ${FULL_IMAGE_NAME}
                                docker push ${LATEST_IMAGE_NAME}
                            """
                        }
                       
                        echo "Docker image built and pushed successfully!"
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
            // Cleanup workspace
            cleanWs()
           
            // The Docker plugin automatically manages image lifecycle
            // No manual cleanup needed - Jenkins will handle it
        }
    }
}
 

