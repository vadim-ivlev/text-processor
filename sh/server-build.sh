#!/bin/bash



echo "Rebuilding Text-processor image..."

docker-compose -f deploy/docker-compose.yml build 

