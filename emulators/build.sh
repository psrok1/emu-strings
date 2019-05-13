#!/bin/bash

# Checking docker version

docker -v
if [ $? -ne 0 ]; then
    echo "Docker not installed!"
    exit 1
fi

# Building wine

(
    cd winedrop &&
    docker build . -t winedrop
) || exit 1

# Exporting to ./images

(
    mkdir -p images &&
    cd images &&
    docker save winedrop -o winedrop.tar &&
    chmod 644 winedrop.tar
) || exit 1
