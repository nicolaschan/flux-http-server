# Set the Docker image name and tag
IMAGE_NAME := "flux-http-server"
IMAGE_TAG := "latest"

# Default command (runs when you just type 'just')
default:
    @just --list

# Build the Docker image
build:
    docker build -t {{IMAGE_NAME}}:{{IMAGE_TAG}} .

# Run the Docker container
run:
  docker run -it \
    --rm \
    -p 8080:8080 \
    -v $HOME/.cache/huggingface:/root/.cache/huggingface \
    --gpus all \
    {{IMAGE_NAME}}:{{IMAGE_TAG}}

# Build and run the Docker container
build-and-run: build run
