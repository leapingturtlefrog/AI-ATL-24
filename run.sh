#!/bin/bash

IMAGE_NAME=image_a

CONTAINER_NAME=container_a

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then

        echo "Starting existing container $CONTAINER_NAME..."

        docker start $CONTAINER_NAME

else
        echo "Building the Docker image"

        docker build -t $IMAGE_NAME .

        echo "Running a new container"

        # docker run --name $CONTAINER_NAME -p 8501:8501 --rm -it --privileged $IMAGE_NAME

        # The following command will only work on true Linux and probably Mac becuase /dev/snd is nonexistent on WSL.
        # Basically, the Docker container can't access the audio input devices, and this command *should* maybe give it permissions
        docker run --name $CONTAINER_NAME -p 8501:8501 --rm -it --privileged --network host --device /dev/snd --group-add audio $IMAGE_NAME
fi
