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
       
        stage('Build & Push Docker Image') {
            steps {
                script {
                    // Use Docker Pipeline plugin to build and push
                    dockerImage = docker.build("${FULL_IMAGE_NAME}", ".")
                   
                    // Run tests inside container (optional - uncomment when tests are ready)
                    // dockerImage.inside {
                    //     sh 'pytest tests/'
                    // }
                   
                    // Push to ACR using Docker plugin
                    docker.withRegistry("https://${ACR_REGISTRY}", "${ACR_CREDENTIALS_ID}") {
                        dockerImage.push("${IMAGE_TAG}")
                        dockerImage.push("latest")
                    }
                   
                    echo "Docker image built and pushed successfully!"
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
