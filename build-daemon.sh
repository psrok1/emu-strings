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

( cd wine-source && ./configure && make -j4 ) || exit 1

# Installing Wine dependencies

export WINE=${PWD}/wine-source/wine
export WINEPREFIX=${PWD}/daemon/wine-prefix

echo "#######################################################"
echo "# Now install all components you are asked for        #"
echo "# EXCEPT wine-mono and wine-gecko (they are optional) #"
echo "#######################################################"

./tools/winetricks mdac27 wsh57

# Prepare daemon image context

(
    mkdir -p daemon/wine-build
    cd wine-source
    find . -name \*.so -exec cp --parents '{}' ../daemon/wine-build -v \;
    find . -name \*.so.* -exec cp --parents '{}' ../daemon/wine-build -v \;
    find . -name \*.fake -exec cp --parents '{}' ../daemon/wine-build -v \;
    cp --parents loader/wine ../daemon/wine-build/ -v
    cp --parents server/wineserver ../daemon/wine-build/ -v
    cp ./wine ../daemon/wine-build -v
)

# Build docker image

(
    cd daemon
    docker build . -t winedrop
)
