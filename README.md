<p align="center">
  <img src="src/web/src/logo.jpg">
</p>

**Emu-strings** - JScript/VBScript malware analyzer based on native Windows Script Host engine.

The main idea is to provide a tool which reveal all useful *strings* that occur during script execution. In most cases, strings are heavily obfuscated and evaluated at runtime. These are including useful IoCs such as distribution site URLs, OLE Automation object identifiers, eval'ed code snippets etc.

[example]

Solution is based on binary-instrumented Windows Script Host engine which is executed in Wine environment. Wine is running inside Docker containers providing separation between concurrently executing instances. 

Network connections made by malware are diverted to simple fakenet, which includes HTTP and DNS service. HTTP server is returning only `500 Internal Server Error` responses, giving script a chance to contact with fallback sites. 

## Requirements

* Linux kernel >= 4.11 (supporting `ip_unprivileged_port_start` sysctl)
* Docker & Docker Compose installed
* at least 8 GB of RAM (recommended 16 GB)
 
Actual requirements are depending on the number of parallel Winedrop instances and DinD configuration.

## Installation

The first step is to clone repository including submodules:

```bash
$ git clone --recurse-submodules https://github.com/psrok1/emu-strings.git
```

Then build an Winedrop image. This may take a while because all components will be build from scratch (including Wine).

```bash
$ cd emulators ; ./build.sh 
```

Finally we can configure and build the emu-strings engine. Start with customizing `docker-compose.yml` depending on your needs. See a few tips below:

* Web interface is exposed at `64205` port. If you want to change that, modify `emu-app` service settings. 
* If you are running in low-memory environment, consider turning off tmpfs mount of `/var/lib/docker` in DinD container. This will drastically drop analysis performance, but will make you save few gigabytes of memory.

After customizing `docker-compose.yml` just build application and run.

```bash
$ docker-compose up --build
```

Web interface in default configuration can be found at `http://127.0.0.1:64205`

## Usage



## Disclaimer


