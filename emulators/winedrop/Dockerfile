# STAGE 1 === === === ===
# Building wine from sources
FROM i386/ubuntu AS winedrop-build
RUN apt update && apt install -y build-essential gcc-multilib flex bison libxi-dev libfreetype6-dev libxcursor-dev libxrandr-dev libxcomposite-dev libtiff5-dev libxrender-dev libxml2-dev libxslt1-dev libjpeg-dev
COPY wine-source /opt/wine-source
WORKDIR /opt/wine-source
RUN ( if [ ! -f ./wine-source/Makefile ]; then ./configure; else true; fi; ) && make -j4

# STAGE 2 === === === ===
# Building monitor image
FROM i386/ubuntu AS winedrop-build-monitor
RUN apt update -y && apt -y install mingw-w64 make
ADD ./monitor /opt/monitor
WORKDIR /opt/monitor
RUN make

# STAGE 3 === === === ===
# Building emulator image
FROM ubuntu
RUN dpkg --add-architecture i386 && apt update && apt-get install -y gcc-multilib python-pip libxml2:i386 libgnutls30:i386 xvfb:i386 wget cabextract
WORKDIR /opt/wine-source
COPY --from=winedrop-build /opt/wine-source .
# Install Python dependencies for emulator and patches
ADD ./emulator/requirements.txt /opt/emulator/requirements.txt
RUN pip install -r /opt/emulator/requirements.txt
ADD ./patches/requirements.txt /opt/patches/requirements.txt
RUN pip install -r /opt/patches/requirements.txt
# Initialize wine-prefix
ENV WINEDLLOVERRIDES="mscoree,mshtml="
ENV WINEPREFIX="/opt/wine-prefix"
ENV WINE="/opt/wine-source/wine"
RUN echo `head -c 500 /dev/urandom | tr -dc 'a-zA-Z0-9_' | fold -w 8 | head -n 1` > /opt/.username
RUN export USER=`cat /opt/.username` && xvfb-run -a ./wine wineboot -u ; while [ ! -z `pidof wineserver` ]; do ( echo "Waiting for wineserver to exit..."; sleep .6 ); done
# Copy winedrop.dll from winedrop-build-monitor and apply patches
ADD ./patches /opt/patches
WORKDIR /opt/patches
COPY --from=winedrop-build-monitor /opt/monitor/winedrop.dll .
RUN export USER=`cat /opt/.username` && xvfb-run -a ./patch.sh
# Set-up emulator daemon
ADD ./emulator /opt/emulator
WORKDIR /opt/analysis
ENTRYPOINT /usr/bin/python /opt/emulator/run.py
