#!/bin/sh
#by 星哥10101

CONFIG_DIR="$HOME/.cargo/"
CONFIG="config"

#install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

#setting to use local source
mkdir -p $CONFIG_DIR
cat > $CONFIG_DIR/$CONFIG <<EOF
[source.crates-io]
replace-with = 'tuna'
[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"
EOF
