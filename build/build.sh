#!/bin/bash

DOCKERFILE="../Dockerfile"

# Generate a random hash tag
TAG=$(openssl rand -hex 4 | tr -d '\n' | head -c 7)

# Latest tag
LATEST_TAG="latest"

# Build the Docker image and tag it with both tags
docker build -t pharmatracker:$TAG -f $DOCKERFILE .. &&
docker tag pharmatracker:$TAG pharmatracker:$LATEST_TAG

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image successfully built and tagged:"
  echo " - Tag: pharmatracker:$TAG"
  echo " - Tag: pharmatracker:$LATEST_TAG"
else
  echo "Failed to build Docker image."
fi
