#!/bin/bash

TARGET="$1"
TOML="Cargo.toml"
BIN="$TARGET/target/release/$TARGET"
DBGBIN="$TARGET/target/debug/$TARGET"

if [ "$TARGET" == '' ]
then
  echo "no target dir!"
  exit 1
fi

cd $TARGET
cargo build
cd -
echo "--------------------"
ls -l $DBGBIN

cp -f $TARGET/$TOML /tmp/
#optimize rust bin for minimum size
echo "[profile.release]" >> $TARGET/$TOML
echo "opt-level='z'" >> $TARGET/$TOML
echo "lto=true" >> $TARGET/$TOML

#build for release
cd $TARGET
cargo build --release
cd -

#strip all symbols
strip $BIN

#Xargo       -- can use Xargo for even smaller bin by e.g. making libstd smaller
#cargo-bloat -- analyze space usage in bin

echo "--------------------"
ls -l $BIN

