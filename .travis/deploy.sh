#!/bin/sh
docker login -u "$REGISTRY_USER" -p "$REGISTRY_PASS"

BRANCH=$(if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then echo $TRAVIS_BRANCH; else echo $TRAVIS_PULL_REQUEST_BRANCH; fi)

docker tag "$IMAGE_NAME" "${IMAGE_NAME}:${BRANCH}"
docker push "${IMAGE_NAME}:${BRANCH}"
