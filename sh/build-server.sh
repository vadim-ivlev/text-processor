#!/bin/bash



echo "Rebuilding Text-processor server image..."

docker-compose -f deploy/docker-compose.yml build 

