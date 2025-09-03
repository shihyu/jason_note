#!/bin/bash

gcc -finstrument-functions -g -c main.c -o main.o
gcc -c trace.c -o trace.o
gcc -no-pie trace.o main.o -o main
