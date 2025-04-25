SUBDIRS ?= docker

# Output docker image
PROJECT_NAME ?= educinfo
AUTHOR ?= doalou
REGISTRY ?= docker.io
BASE_IMAGE_REGISTRY ?= docker.io
WEB_SITE ?= doalo.fr

IMAGE_VERSION ?= 1.0.1
IMAGE_NAME ?= $(PROJECT_NAME)

# Max CPU and memory
CPUS ?= 4.0
CPU_SHARES ?= 1024
MEMORY ?= 8GB
MEMORY_RESERVATION ?= 2GB
TMPFS_SIZE ?= 4GB
BUILD_CPU_SHARES ?= 1024
BUILD_MEMORY ?= 8GB

TEST_CMD ?= "./docker/test/test.sh"
RUN_CMD ?= "flask run --host=0.0.0.0"

include DockerImages.mk
