#!/bin/bash

echo "Testing Docker build..."

# Build the Docker image
echo "Building Docker image..."
docker build -t super-app-backend .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✓ Docker build successful"
    
    # Test running the container
    echo "Testing container startup..."
    docker run --rm -d --name test-container super-app-backend
    
    # Wait a moment for container to start
    sleep 5
    
    # Check container logs
    echo "Container logs:"
    docker logs test-container
    
    # Check if container is running
    if docker ps | grep -q test-container; then
        echo "✓ Container is running"
        
        # Test the health endpoint
        echo "Testing health endpoint..."
        curl -f http://localhost:8000/ping || echo "Health check failed"
        
        # Stop and remove test container
        docker stop test-container
        docker rm test-container
    else
        echo "❌ Container failed to start"
        docker logs test-container
    fi
else
    echo "❌ Docker build failed"
fi 