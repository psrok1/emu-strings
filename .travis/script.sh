#!/bin/bash
BRANCH=$(if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then echo $TRAVIS_BRANCH; else echo $TRAVIS_PULL_REQUEST_BRANCH; fi)

# Pull branch build
if ! ( docker pull "${IMAGE_NAME}:${BRANCH}" ); then 
    # Pull latest if branch doesn't exist yet
    BRANCH="latest"
    if ! ( docker pull "${IMAGE_NAME}:${BRANCH}" ); then
        echo "Previous version not found - building from scratch"
    else
        echo "Pulled ${IMAGE_NAME}:${BRANCH}"
    fi
else
    echo "Pulled ${IMAGE_NAME}:${BRANCH}"
fi

if [ -z "$DOCKERFILE" ]; then
    DOCKERFILE="${DOCKERFILE_PATH}/Dockerfile"
fi

echo "Building ${IMAGE_NAME}:${BRANCH} using $DOCKERFILE"

docker build --pull --cache-from "${IMAGE_NAME}:${BRANCH}" --tag "$IMAGE_NAME" --file "$DOCKERFILE" "$DOCKERFILE_PATH"