# GDB Tracer - Rust Support

This GDB tracer tool now supports both C and Rust programs. The Rust version (`trace_rust.py`) provides specialized functionality for tracing Rust programs.

## Features

### Rust-Specific Enhancements

1. **Automatic Name Demangling**: Rust function names are automatically demangled for readability
2. **Standard Library Filtering**: By default, skips std::, core::, and alloc:: functions to focus on user code
3. **Rust Type Handling**: Better handling of Rust-specific types like String, &str, structs
4. **Method Tracing**: Supports tracing impl methods and associated functions

## Usage

### Building the Rust Demo

```bash
# Build both C and Rust demos
make

# Build only Rust demo
make demo_rust
```

### Running Traces

```bash
# Basic tracing (skips standard library)
make rust-trace

# Auto-trace all user functions
make rust-auto-trace

# Interactive debugging with trace loaded
make rust-debug
```

### GDB Commands

When in interactive GDB mode:

```gdb
# Trace specific functions
rust-trace main calculate add

# Auto-discover and trace all functions
rust-auto-trace

# Include standard library functions
rust-trace --include-std

# Stop tracing
rust-trace-stop
```

## Example Output

```
[14:23:45.123] → main()
[14:23:45.124]   → calculate(a=10, b=20)
[14:23:45.125]     → add(x=10, y=20)
[14:23:45.126]     ← add returned: 30
[14:23:45.127]     → multiply(x=10, y=20)
[14:23:45.128]     ← multiply returned: 200
[14:23:45.129]   ← calculate returned: 230
[14:23:45.130]   → process_string(input="Hello, Rust!")
[14:23:45.131]     → to_uppercase(s="Hello, Rust!")
[14:23:45.132]     ← to_uppercase returned: "HELLO, RUST!"
[14:23:45.133]     → add_suffix(s="HELLO, RUST!", suffix="!!!")
[14:23:45.134]     ← add_suffix returned: "HELLO, RUST!!!!"
[14:23:45.135]   ← process_string returned: "HELLO, RUST!!!!"
[14:23:45.136] ← main returned: ()
```

## Compilation Requirements

For best results, compile Rust programs with debug symbols:

```bash
rustc -g -C opt-level=0 -C debuginfo=2 your_program.rs
```

Or with Cargo:

```toml
[profile.dev]
opt-level = 0
debug = true
```

## Differences from C Version

| Feature | C Version | Rust Version |
|---------|-----------|--------------|
| Function name demangling | Not needed | Automatic |
| Standard library filtering | N/A | Yes (configurable) |
| Type display | Simple | Rust-aware |
| String handling | C strings | String/&str aware |
| Method support | Functions only | Methods + functions |

## Troubleshooting

1. **Functions not found**: Ensure binary is compiled with debug symbols (`-g` flag)
2. **Mangled names**: The tracer automatically demangles, but you can use mangled names directly if needed
3. **Missing traces**: Some inline functions may be optimized out even with `-O0`
4. **Standard library noise**: Use default mode (without `--include-std`) to skip std functions

## Advanced Usage

### Tracing Specific Modules

```gdb
# Trace all functions in a module
rust-trace 'mymodule::*'

# Trace specific impl blocks
rust-trace 'DataStruct::*'
```

### Custom Filtering

Modify `skip_std_lib` logic in `trace_rust.py` to customize which functions to skip:

```python
# Example: Skip external crates
if any(func_name.startswith(prefix) for prefix in ["std::", "core::", "tokio::", "hyper::"]):
    return False
```