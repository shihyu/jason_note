FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    build-essential vim \
    && rm -rf /var/lib/apt/lists/*

VOLUME /usr/src/app

CMD ["/bin/bash"]
