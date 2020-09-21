#!/bin/bash



echo "Rebuilding Text-processor worker image..."

docker-compose -f deploy/docker-compose-worker.yml build 

echo "push the docker image" 
docker login
docker push vadimivlev/text-processor-worker:latest

