#!/bin/bash

dpkg --add-architecture i386
( sudo apt-get update && sudo apt-get install -y build-essential gcc-multilib flex bison libxi-dev:i386 libfreetype6-dev:i386 libxcursor-dev:i386 libxrandr-dev:i386 libxcomposite-dev:i386 libtiff5-dev:i386 libxrender-dev:i386 libxml2-dev:i386 libxslt1-dev:i386 libjpeg-dev:i386 ) || exit 
( cd wine-source && ./configure && make -j4 ) || exit 1
export WINE=${PWD}/wine-source/wine
export WINEPREFIX=${PWD}/wine-prefix
./tools/winetricks mdac27
