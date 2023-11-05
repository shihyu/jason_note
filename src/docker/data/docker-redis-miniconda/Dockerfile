FROM redis

RUN apt-get update && apt-get install -y vim tmux htop redis-server wget build-essential

ARG CONDA_VERSION=py310_23.9.0-0

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN conda install -c conda-forge ta-lib

RUN mkdir -p /usr/src/app

COPY *.py /usr/src/app

WORKDIR /usr/src/app/
