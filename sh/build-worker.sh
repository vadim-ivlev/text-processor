#!/bin/bash



echo "Rebuilding Text-processor worker image..."

docker-compose -f deploy/docker-compose-worker.yml build 

