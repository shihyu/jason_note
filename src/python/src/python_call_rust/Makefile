# Makefile

RUST_SRC = lib.rs
RUST_TARGET = lib.so

.PHONY: all clean

all: $(RUST_TARGET)

$(RUST_TARGET): $(RUST_SRC)
	rustc --crate-type cdylib $<

clean:
	rm -f $(RUST_TARGET)

