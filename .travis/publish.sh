#!/bin/bash

docker login -u "$REGISTRY_USER" -p "$REGISTRY_PASS"

BRANCH=$(if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then echo $TRAVIS_BRANCH; else echo $TRAVIS_PULL_REQUEST_BRANCH; fi)
IMAGES=("psrok1/winedrop" "psrok1/emu-strings-boxjs" "psrok1/emu-strings" "psrok1/emu-strings-daemon")

for image in ${IMAGES[*]}
do
  docker pull "${image}:${BRANCH}"
  docker tag "${image}:${BRANCH}" "${image}:latest"
  docker push "${image}:latest"
done