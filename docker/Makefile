# Base image
BASE_IMAGE_REGISTRY ?= docker.io
BASE_IMAGE_PATH ?= 
BASE_IMAGE_NAME ?= python
BASE_IMAGE_TAGS ?= 3.12-slim-bookworm

# Output docker image
AUTHOR ?= doalou
WEB_SITE ?= doalo.fr

OUTPUT_IMAGE_REGISTRY ?= docker.io
OUTPUT_IMAGE_PATH ?= doalou
OUTPUT_IMAGE_NAME ?= educinfo
OUTPUT_IMAGE_VERSION ?= 1.1.0

WORKDIR ?= /work

# Max CPU and memory
CPUS ?= 8.0
CPU_SHARES ?= 1024
MEMORY ?= 16GB
MEMORY_RESERVATION ?= 2GB
TMPFS_SIZE ?= 4GB
BUILD_CPU_SHARES ?= 1024
BUILD_MEMORY ?= 16GB

TEST_CMD ?= "./docker/test/test.sh"
RUN_CMD ?= "flask run --host=0.0.0.0"

include DockerImage.mk
