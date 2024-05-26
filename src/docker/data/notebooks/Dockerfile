FROM jupyter/base-notebook:python-3.11

ENV APP_HOME=$HOME/work
WORKDIR $APP_HOME

# Copy requirements file
COPY ./requirements.txt requirements.txt

# Install Python packages and PyTorch with CUDA support
RUN pip install -r requirements.txt && \
    conda install -y pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

USER root

# Install build dependencies and TA-Lib
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential \
        curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -SL https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz | tar -xzC . && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    pip install TA-Lib && \
    rm -rf ta-lib* && \
    rm -rf /root/.cache/* && \
    apt-get clean && \
    apt-get autoremove -y

WORKDIR $APP_HOME
USER $NB_UID
