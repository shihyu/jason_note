FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    vim \
    git \
    autoconf \
    automake \
    autotools-dev \
    ninja-build \
    libmpc-dev \
    libmpfr-dev \
    libgmp-dev \
    libglib2.0-dev \
    libpixman-1-dev \
    libncurses5-dev \
    libtool \
    libexpat-dev \
    zlib1g-dev \
    curl \
    gawk \
    bison \
    flex \
    texinfo \
    gperf \
    patchutils \
    bc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
VOLUME /usr/src/app

# Set default command
CMD ["/bin/bash"]
