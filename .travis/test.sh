#!/bin/sh

export TAG
TAG=$(if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then echo $TRAVIS_BRANCH; else echo $TRAVIS_PULL_REQUEST_BRANCH; fi)

pip install -r tests/requirements.txt

docker-compose pull && \
docker-compose up -d && \
sleep 5 && \
python tests/test.py
