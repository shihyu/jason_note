# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Buttplug-js contains two interconnected projects for controlling intimate devices via Bluetooth and other protocols:
- **JS Client** (`js/`): TypeScript client library for connecting to Buttplug servers
- **WASM Module** (`wasm/`): WebAssembly-compiled Rust server with WebBluetooth support

## Build Commands

### JS Client (`js/` directory)
```bash
# Install dependencies
npm install

# Build everything (CommonJS + Web)
npm run build

# Build for Node.js only
npm run build:main

# Build for web only  
npm run build:web

# Run tests
npm test

# Run web-specific tests
npm run web-test

# Generate documentation
npm run build:doc

# Lint code
npm run lint
```

### WASM Module (`wasm/` directory)
```bash
# Install dependencies
npm install

# Build WASM from Rust (requires wasm-pack)
npm run build:wasm

# Build TypeScript wrapper
npm run build:main

# Build web bundle
npm run build:web
```

### Example Server (`wasm/example/` directory)
```bash
# Install and run example
npm install
python3 -m http.server 7777
# Navigate to http://localhost:7777/[filename].html
```

## Architecture

### Message Protocol
The codebase uses a message-based architecture where clients communicate with servers via WebSocket using typed messages defined in `js/src/core/Messages.ts`. Key message types:
- `RequestServerInfo`, `ServerInfo`: Handshake and capability negotiation
- `StartScanning`, `StopScanning`: Device discovery control
- `RequestDeviceList`, `DeviceList`: Device enumeration
- `ScalarCmd`, `LinearCmd`, `RotateCmd`: Device control commands

### Client-Server Communication Flow
1. Client creates `ButtplugClient` instance
2. Connects via connector (WebSocket, WASM, etc.)
3. Performs handshake to establish protocol version
4. Scans for devices or requests device list
5. Controls devices through command messages
6. Handles events via EventEmitter pattern

### Key Abstractions

**Client Side (`js/src/client/`)**:
- `Client.ts`: Main client class managing connection and devices
- `ButtplugClientDevice.ts`: Device abstraction with control methods
- `IButtplugClientConnector.ts`: Interface for different connection types
- `ButtplugBrowserWebsocketClientConnector.ts`: Browser WebSocket implementation
- `ButtplugNodeWebsocketClientConnector.ts`: Node.js WebSocket implementation

**WASM Integration (`wasm/src/`)**:
- `ButtplugWasmClientConnector.ts`: Bridges JS client to WASM server
- Rust code in `wasm/rust/` handles WebBluetooth directly
- Uses `wasm-bindgen` for JS-Rust interop

### WebBluetooth Device Support
The WASM module provides WebBluetooth support through:
- `webbluetooth_manager.rs`: Device discovery and management
- `webbluetooth_hardware.rs`: Low-level Bluetooth communication
- Common service UUIDs for adult devices are pre-configured

## Development Notes

### TypeScript Configuration
- Target: ES6 with CommonJS modules for Node
- Strict null checks enabled
- Decorators enabled for serialization
- Source maps included in builds

### Testing Approach
- Unit tests in `tests/` use Jest with ts-jest
- Web tests in `web-tests/` use Puppeteer for browser automation
- Mock WebSocket server for testing client connections

### Build Output Structure
```
js/dist/
├── main/       # CommonJS for Node.js
└── web/        # UMD and ES modules for browsers
    ├── buttplug.js     # UMD bundle
    └── buttplug.mjs    # ES module

wasm/dist/
└── buttplug-wasm.mjs   # ES module with embedded WASM (1.5-5MB)
```

### Common Development Tasks

**Adding Bluetooth Device Support**:
1. Update service/characteristic UUIDs in connection requests
2. Implement command encoding for device protocol
3. Test with real hardware using example pages

**Debugging WebBluetooth Issues**:
- Use Chrome/Edge DevTools for Web Bluetooth debugging
- Check chrome://bluetooth-internals for device details
- Ensure all required service UUIDs are in `optionalServices`

**WASM Build Troubleshooting**:
- Rust compilation errors often relate to `time` crate version conflicts
- Ensure `wasm-pack` is installed: `cargo install wasm-pack`
- WASM builds require Rust toolchain with `wasm32-unknown-unknown` target

### Protocol Documentation
Full Buttplug protocol specification: https://buttplug-spec.docs.buttplug.io/

### Version Compatibility
- JS Client: v3.2.2
- WASM: v2.0.1  
- Protocol: Buttplug v3
- Minimum Node.js: 10.0