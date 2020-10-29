#!/bin/bash



echo "Rebuilding Text-processor image..."
docker build -t vadimivlev/text-processor:latest -f ./Dockerfile . 

echo "Pushing the image to hub.docker.com" 
docker login
docker push vadimivlev/text-processor:latest

