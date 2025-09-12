.PHONY: all build release test clean run bench

all: build

build:
	cargo build

release:
	cargo build --release

test:
	cargo test

run:
	cargo run --release

bench:
	cargo bench

clean:
	cargo clean
	rm -f *.txt *.log