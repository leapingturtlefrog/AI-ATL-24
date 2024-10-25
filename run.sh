#!/bin/bash

# Run with the command './run.sh'
# Builds the Docker image and runs a new container.

IMAGE_NAME=image_a
CONTAINER_NAME=container_a
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
	echo "Starting existing container $CONTAINER_NAME..."
	docker start $CONTAINER_NAME
else
	echo "Building the Docker image"
	docker build -t $IMAGE_NAME .
	echo "Running a new container"
	docker run --name $CONTAINER_NAME -p 8501:8501 --rm -it $IMAGE_NAME
fi
