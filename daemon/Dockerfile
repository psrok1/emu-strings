FROM ubuntu:16.04

ADD . /root/daemon
RUN apt-get update && apt-get install -y gcc-multilib python-pip && pip install -r /root/daemon/requirements.txt

WORKDIR /root/analysis
ENTRYPOINT /usr/bin/python /root/daemon/run.py
