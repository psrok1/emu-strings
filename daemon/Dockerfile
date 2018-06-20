FROM ubuntu:16.04

RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y gcc-multilib python-pip libxml2:i386 libgnutls30:i386
ADD ./requirements.txt /root/daemon/requirements.txt
RUN pip install -r /root/daemon/requirements.txt

ADD . /root/daemon/
WORKDIR /root/analysis
ENTRYPOINT /usr/bin/python /root/daemon/run.py
