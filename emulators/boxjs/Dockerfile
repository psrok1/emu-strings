FROM node:8-alpine

RUN apk update && apk upgrade
RUN apk add file gcc m4

WORKDIR /opt/emulator
ADD emulator .

WORKDIR /opt/emulator/box-js
RUN rm -rf .git && npm install

WORKDIR /opt/analysis
ENTRYPOINT node /opt/emulator/run.js
