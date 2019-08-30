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
    docker build . -t psrok1/winedrop
) || exit 1

# Exporting to ./images

echo Exporting winedrop to ./images... this may take a while.
(
    mkdir -p images &&
    cd images &&
    docker save psrok1/winedrop -o winedrop.tar &&
    chmod 644 winedrop.tar
) || exit 1
