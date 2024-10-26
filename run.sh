#!/bin/bash

OS_NAME=$(uname -s)
IMAGE_NAME=image_a
CONTAINER_NAME=container_a

if [ "$OS_NAME" == "Linux" ]; then
    DOCKER_COMMAND="docker run -t -i -e "PULSE_SERVER=${PULSE_SERVER}" -v /mnt/wslg/:/mnt/wslg/ --name $CONTAINER_NAME -p 8501:8501 --rm -it --privileged $IMAGE_NAME"
elif [ "$OS_NAME" == "Darwin" ]; then
    DOCKER_COMMAND="docker run --name $CONTAINER_NAME -p 8501:8501 --rm -it $IMAGE_NAME"
else
    echo "Unsupported operating system: $OS_NAME"
    exit 1
fi

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then    echo "Starting existing container $CONTAINER_NAME..."
    docker start $CONTAINER_NAME
else
    echo "Building the Docker image"
    docker build -t $IMAGE_NAME .
    echo "Running a new container"
    eval $DOCKER_COMMAND
fi

