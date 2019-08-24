# STAGE 1 === === === ===
# Building monitor image
FROM i386/ubuntu AS winedrop-build-monitor
RUN apt update -y && apt -y install mingw-w64 make
ADD ./monitor /opt/monitor
WORKDIR /opt/monitor
RUN make

# STAGE 2 === === === ===
# Building emulator image
FROM ubuntu
RUN dpkg --add-architecture i386 && apt update && apt-get install -y gcc-multilib python-pip libxml2:i386 libgnutls30:i386 xvfb:i386 wget cabextract
# Install Python dependencies for emulator and patches
ADD ./emulator/requirements.txt /opt/emulator/requirements.txt
RUN pip install -r /opt/emulator/requirements.txt
ADD ./patches/requirements.txt /opt/patches/requirements.txt
RUN pip install -r /opt/patches/requirements.txt
# Switch to unprivileged user
RUN groupadd -g 9999 emustrings && \
    useradd -r -d /opt -u 9999 -g emustrings emustrings && \
    chown -R emustrings:emustrings /opt
USER emustrings
# Initialize wine-prefix
WORKDIR /opt/wine-dist
COPY --from=psrok1/wine-modified /opt/wine-dist .
ENV WINEDLLOVERRIDES="mscoree,mshtml="
ENV WINEPREFIX="/opt/wine-prefix"
ENV WINE="/opt/wine-dist/usr/local/bin/wine"
RUN echo `head -c 500 /dev/urandom | tr -dc 'a-zA-Z0-9_' | fold -w 8 | head -n 1` > /opt/.username
RUN export USER=`cat /opt/.username` \
    && xvfb-run -a $WINE wineboot -u ; \
    while [ ! -z `pidof wineserver` ]; \
        do ( echo "Waiting for wineserver to exit..."; sleep .6 ); done
# Copy winedrop.dll from winedrop-build-monitor and apply patches
ADD ./patches /opt/patches
WORKDIR /opt/patches
COPY --from=winedrop-build-monitor /opt/monitor/winedrop.dll .
RUN export USER=`cat /opt/.username` && \
    wget -O- https://raw.githubusercontent.com/Winetricks/winetricks/ccc1c48ffa750c18eec1da317ac392934b68844f/src/winetricks | \
    sed '0,/WINETRICKS_LIB/ s/WINETRICKS_LIB/no_WINETRICKS_LIB/' > winetricks && \
    chmod +x winetricks && \
    xvfb-run -a ./patch.sh && \
    rm winetricks
# Set-up emulator daemon
ADD ./emulator /opt/emulator
WORKDIR /opt/analysis
ENTRYPOINT /usr/bin/python /opt/emulator/run.py
