FROM debian:10.8-slim

RUN apt-get update
RUN apt update && apt-get install -y \
    bc \
    bison \
    build-essential \
    cpio \
    flex \
    libelf-dev \
    libncurses-dev \
    libssl-dev \
    vim-tiny \
    vim \
    qemu-kvm \
    gdb
ADD ./start-gdb.sh /usr/local/bin
ADD ./build-kernel.sh /usr/local/bin
RUN chmod a+x /usr/local/bin/*.sh
WORKDIR /workspace
