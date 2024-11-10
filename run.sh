#! /bin/bash
# This script is used to setup the development environment for the project on a new machine
# It will install the required packages and setup the virtual environment
bash setup_dev_env.sh

# Build the Docker image
docker build -t daiigr/buddy-matcher:latest .

echo "Docker image built successfully"


# Remove any existing buddy-matcher container
docker rm buddy-matcher 2>/dev/null || true

echo "running the container"
# Run the Docker container
docker run  \
  --name buddy-matcher \
  -v "$(pwd)/config:/config" \
  -v "$(pwd)/input:/input" \
  -v "$(pwd)/output:/output" \
  daiigr/buddy-matcher:latest
