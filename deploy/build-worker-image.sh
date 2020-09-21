#!/bin/bash

echo "build a docker image"
docker build -t vadimivlev/text-processor-worker:latest -f Dockerfile-worker . 

echo "push the docker image" 
docker login
docker push vadimivlev/text-processor-worker:latest

