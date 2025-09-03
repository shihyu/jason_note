.PHONY: all build clean flutter-build rust-build

# Default target
all: build

# Build everything
build: rust-build flutter-build

# Build Rust bridge
rust-build:
	cargo build

# Build Flutter (from parent directory)
flutter-build:
	cd .. && flutter build linux

# Clean all build artifacts
clean:
	cargo clean
	rm -rf target
	cd .. && flutter clean
	rm -rf ../build

# Help target
help:
	@echo "Available targets:"
	@echo "  build        - Build both Rust bridge and Flutter app"
	@echo "  rust-build   - Build only the Rust bridge"
	@echo "  flutter-build - Build only the Flutter app"
	@echo "  clean        - Clean all build artifacts"
	@echo "  help         - Show this help message"