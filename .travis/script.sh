#!/bin/sh
BRANCH=$(if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then echo $TRAVIS_BRANCH; else echo $TRAVIS_PULL_REQUEST_BRANCH; fi)

# Pull branch build
if ! ( docker pull "${IMAGE_NAME}:${BRANCH}" ); then 
    # Pull latest if branch doesn't exist yet
    BRANCH="latest"
    docker pull "${IMAGE_NAME}:${BRANCH}" || true
fi

if [[ ! -d "$DOCKERFILE "]]; then
    DOCKERFILE="${DOCKERFILE_PATH}/Dockerfile"
fi

docker build --pull --cache-from "${IMAGE_NAME}:${BRANCH}" --tag "$IMAGE_NAME" --file "$DOCKERFILE" "$DOCKERFILE_PATH"