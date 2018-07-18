#!/bin/bash

# Checking docker version

docker -v
if [ $? -ne 0 ]; then
    echo "Docker not installed!"
    exit 1
fi

# Installing build dependencies

sudo dpkg --add-architecture i386
( sudo apt-get update && sudo apt-get install -y build-essential gcc-multilib flex bison libxi-dev:i386 libfreetype6-dev:i386 libxcursor-dev:i386 libxrandr-dev:i386 libxcomposite-dev:i386 libtiff5-dev:i386 libxrender-dev:i386 libxml2-dev:i386 libxslt1-dev:i386 libjpeg-dev:i386 ) || exit 

# Building wine

if [ "$1" == "all" ] || [ ! -f ./wine-source/Makefile ]; then
    ( cd wine-source && ./configure ) || exit 1
fi

( cd wine-source && make -j4 ) || exit 1

# Installing Wine dependencies

(
    export USER=winedrop
    export WINE=${PWD}/wine-source/wine
    export WINEARCH=win32
    export WINEPREFIX=${PWD}/emulator/wine-prefix

    echo "#######################################################"
    echo "# Now install all components you are asked for        #"
    echo "# EXCEPT wine-mono and wine-gecko (they are optional) #"
    echo "#######################################################"

    ./tools/winetricks mdac27 wsh57
) || exit 1

# Prepare emulator image context

(
    mkdir -p emulator/wine-build
    cd wine-source
    find . -name \*.so -exec cp --parents '{}' ../emulator/wine-build -v \;
    find . -name \*.so.* -exec cp --parents '{}' ../emulator/wine-build -v \;
    find . -name \*.fake -exec cp --parents '{}' ../emulator/wine-build -v \;
    cp --parents loader/wine ../emulator/wine-build/ -v
    cp --parents server/wineserver ../emulator/wine-build/ -v
    cp ./wine ../emulator/wine-build -v
)

# Build docker image

(
    cd emulator
    docker build . -t winedrop
)
