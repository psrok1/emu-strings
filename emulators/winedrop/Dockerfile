# STAGE 1 === === === ===
# Building wine from sources
FROM i386/ubuntu AS winedrop-build
RUN apt update && apt install -y build-essential gcc-multilib flex bison libxi-dev libfreetype6-dev libxcursor-dev libxrandr-dev libxcomposite-dev libtiff5-dev libxrender-dev libxml2-dev libxslt1-dev libjpeg-dev
COPY wine-source /opt/wine-source
WORKDIR /opt/wine-source
RUN ( if [ ! -f ./wine-source/Makefile ]; then ./configure; else true; fi; ) && make -j4

# STAGE 2 === === === ===
# Building emulator image
FROM i386/ubuntu
RUN apt update && apt install -y gcc-multilib python-pip libxml2 libgnutls30 xvfb wget cabextract
ADD ./emulator/requirements.txt /opt/emulator/requirements.txt
RUN pip install -r /opt/emulator/requirements.txt
ADD ./patches/requirements.txt /opt/patches/requirements.txt
RUN pip install -r /opt/patches/requirements.txt

WORKDIR /opt/wine-source
COPY --from=winedrop-build /opt/wine-source .
ENV WINEDLLOVERRIDES="mscoree,mshtml="
ENV WINEPREFIX="/opt/wine-prefix"
ENV WINE="/opt/wine-source/wine"
RUN echo `head -c 500 /dev/urandom | tr -dc 'a-zA-Z0-9_' | fold -w 8 | head -n 1` > /opt/.username
RUN export USER=`cat /opt/.username` && xvfb-run -a ./wine wineboot -u ; while [ ! -z `pidof wineserver` ]; do ( echo "Waiting for wineserver to exit..."; sleep .6 ); done

ADD ./patches /opt/patches
WORKDIR /opt/patches
RUN export USER=`cat /opt/.username` && xvfb-run -a ./patch.sh

ADD ./emulator /opt/emulator
WORKDIR /opt/analysis
ENTRYPOINT /usr/bin/python /opt/emulator/run.py
