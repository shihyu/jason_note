set -e

gcc -march=native -O3 -fomit-frame-pointer -fverbose-asm -S main.cpp -o /tmp/main.S
vim /tmp/main.S
