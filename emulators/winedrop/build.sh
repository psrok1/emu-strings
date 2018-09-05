#!/bin/bash

# Checking docker version

docker -v
if [ $? -ne 0 ]; then
    echo "Docker not installed!"
    exit 1
fi

# Building wine

(
    docker build .
) || exit 1
