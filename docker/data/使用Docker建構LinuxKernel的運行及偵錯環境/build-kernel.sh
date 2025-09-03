#!/bin/bash

cd /workspace/linux-5.12.14
make O=../obj/linux/ -j$(nproc)
