#!/bin/bash

echo "build a docker image"
docker build -t vadimivlev/text-processor:latest -f Dockerfile . 

echo "push the docker image" 
docker login
docker push vadimivlev/text-processor-worker:latest

