#!/usr/bin/env python3
# trace_rust.py - GDB Python script for tracing Rust program execution

import gdb
import datetime
import re

# Global variables for tracking indent level
indent_level = 0
trace_file = None
skip_std_lib = True  # Skip standard library functions by default

class RustFunctionTracer(gdb.Breakpoint):
    """Set breakpoint at function entry and log"""

    def __init__(self, function_name):
        super().__init__(function_name)
        self.function_name = function_name

    def stop(self):
        global indent_level, trace_file, skip_std_lib

        # Get current frame info
        frame = gdb.selected_frame()

        # Skip standard library functions if configured
        if skip_std_lib:
            func_name = str(frame.name() or self.function_name)
            # Skip std::, core::, alloc:: functions
            if any(func_name.startswith(prefix) for prefix in ["std::", "core::", "alloc::", "_ZN3std", "_ZN4core", "_ZN5alloc"]):
                return False

        # Get function arguments
        args = []
        try:
            block = frame.block()
            for symbol in block:
                if symbol.is_argument:
                    try:
                        value = frame.read_var(symbol)
                        # Handle Rust types better
                        value_str = str(value)
                        # Simplify complex Rust types
                        if len(value_str) > 50:
                            value_str = value_str[:47] + "..."
                        args.append(f"{symbol.name}={value_str}")
                    except:
                        args.append(f"{symbol.name}=<?>")
        except:
            # Try to get from frame info
            try:
                # For Rust, arguments might be mangled
                info = gdb.execute(f"info args", to_string=True)
                if info and "No arguments" not in info:
                    for line in info.split('\n'):
                        if '=' in line:
                            args.append(line.strip())
            except:
                pass

        # Demangle Rust function names
        demangled_name = demangle_rust_name(self.function_name)

        # Format output
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        indent = "  " * indent_level
        message = f"[{timestamp}] {indent}→ {demangled_name}({', '.join(args)})"

        # Output to terminal and file
        print(message)
        if trace_file:
            trace_file.write(message + "\n")
            trace_file.flush()

        # Increase indent level
        indent_level += 1

        # Set function return breakpoint
        try:
            RustFunctionExitTracer(frame, demangled_name)
        except:
            pass

        # Don't stop execution
        return False

class RustFunctionExitTracer(gdb.FinishBreakpoint):
    """Log when function returns"""

    def __init__(self, frame, function_name=None):
        try:
            super().__init__(frame)
            self.function_name = function_name or demangle_rust_name(frame.name())
        except Exception as e:
            pass

    def stop(self):
        global indent_level, trace_file

        # Decrease indent level
        indent_level = max(0, indent_level - 1)

        # Get return value
        try:
            return_value = str(self.return_value)
            # Simplify complex Rust return values
            if len(return_value) > 50:
                return_value = return_value[:47] + "..."
        except:
            return_value = "<unknown>"

        # Format output
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        indent = "  " * indent_level
        message = f"[{timestamp}] {indent}← {self.function_name} returned: {return_value}"

        # Output to terminal and file
        print(message)
        if trace_file:
            trace_file.write(message + "\n")
            trace_file.flush()

        # Don't stop execution
        return False

    def out_of_scope(self):
        # Handle out of scope case
        global indent_level
        indent_level = max(0, indent_level - 1)
        return False

def demangle_rust_name(name):
    """Demangle Rust function names"""
    if not name:
        return "<unknown>"

    # Try using GDB's built-in demangler
    try:
        demangled = gdb.execute(f"demangle {name}", to_string=True).strip()
        if demangled and not demangled.startswith("Can't demangle"):
            # Clean up the output
            lines = demangled.split('\n')
            for line in lines:
                if '=' in line or 'is' in line:
                    # Extract the demangled name after '=' or 'is'
                    parts = line.split('=' if '=' in line else 'is', 1)
                    if len(parts) > 1:
                        clean_name = parts[1].strip()
                        # Remove memory addresses if present
                        clean_name = re.sub(r'\s+at\s+0x[0-9a-fA-F]+', '', clean_name)
                        return clean_name
            return demangled
    except:
        pass

    # If GDB demangling fails, try basic cleanup
    # Remove common Rust mangling prefixes
    if name.startswith("_ZN"):
        # Basic Rust demangling
        # Format: _ZN<length><name>...
        try:
            # Simple extraction of module::function pattern
            parts = name.split("$")
            if parts:
                return parts[0].replace("_ZN", "").replace("17h", "::h")
        except:
            pass

    return name

class RustTraceCommand(gdb.Command):
    """Start tracing Rust program execution"""

    def __init__(self):
        super().__init__("rust-trace", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        global trace_file, indent_level, skip_std_lib

        # Parse arguments
        args = arg.split() if arg else []

        # Check for --include-std flag
        if "--include-std" in args:
            skip_std_lib = False
            args.remove("--include-std")
            print("Including standard library functions in trace")
        else:
            skip_std_lib = True
            print("Skipping standard library functions (use --include-std to include)")

        # Open log file
        trace_file = open("rust_trace_log.txt", "w")
        trace_file.write(f"=== Rust trace started at {datetime.datetime.now()} ===\n")

        # Clear old breakpoints
        try:
            gdb.execute("delete breakpoints")
        except:
            pass

        # Reset indent level
        indent_level = 0

        # If specific functions provided, use them
        if args:
            functions = args
        else:
            # Try to auto-discover Rust functions
            functions = discover_rust_functions()

        # Set breakpoints
        traced_count = 0
        for func in functions:
            try:
                RustFunctionTracer(func)
                demangled = demangle_rust_name(func)
                print(f"✓ Tracing function: {demangled}")
                traced_count += 1
            except Exception as e:
                print(f"✗ Could not trace: {func} - {e}")

        print(f"\nRust tracing started. Tracing {traced_count} functions.")
        print("Output will be saved to rust_trace_log.txt")
        print("Use 'continue' to run the program\n")

def discover_rust_functions():
    """Auto-discover Rust functions in the binary"""
    functions = set()

    try:
        # Get all functions from the binary
        result = gdb.execute("info functions", to_string=True)

        for line in result.split('\n'):
            # Look for Rust-style mangled names or demangled names
            if '::' in line or '_ZN' in line:
                # Extract function name
                if ':' in line and '(' in line:
                    try:
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            func_def = parts[1].strip()
                            if '(' in func_def:
                                before_paren = func_def.split('(')[0]
                                words = before_paren.split()
                                if words:
                                    func_name = words[-1].strip('*')
                                    # Filter out obvious standard library functions
                                    if (func_name and
                                        not func_name.startswith('_ZN3std') and
                                        not func_name.startswith('_ZN4core') and
                                        not func_name.startswith('_ZN5alloc')):
                                        functions.add(func_name)
                    except:
                        pass
    except:
        pass

    # If no functions found, try alternative method
    if not functions:
        try:
            # Look for main and common Rust patterns
            for pattern in ["main", "^[a-z_][a-z0-9_]*::", "_ZN.*E$"]:
                try:
                    result = gdb.execute(f"info functions {pattern}", to_string=True)
                    for line in result.split('\n'):
                        if '(' in line and ':' in line:
                            try:
                                parts = line.split(':')[1].strip()
                                if '(' in parts:
                                    name = parts.split('(')[0].strip().split()[-1]
                                    if name:
                                        functions.add(name)
                            except:
                                pass
                except:
                    pass
        except:
            pass

    # Default to main if nothing found
    if not functions:
        functions = {"main"}

    return list(functions)

class RustStopTraceCommand(gdb.Command):
    """Stop tracing"""

    def __init__(self):
        super().__init__("rust-trace-stop", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        global trace_file, indent_level

        # Delete all breakpoints
        try:
            gdb.execute("delete breakpoints")
        except:
            pass

        # Reset indent level
        indent_level = 0

        # Close file
        if trace_file:
            trace_file.write(f"=== Rust trace ended at {datetime.datetime.now()} ===\n")
            trace_file.close()
            trace_file = None

        print("Rust tracing stopped")

class RustAutoTraceCommand(gdb.Command):
    """Auto-trace all user Rust functions"""

    def __init__(self):
        super().__init__("rust-auto-trace", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        # Just call rust-trace without specific functions
        gdb.execute(f"rust-trace {arg}")

# Register commands
RustTraceCommand()
RustStopTraceCommand()
RustAutoTraceCommand()

print("""
╔════════════════════════════════════════════╗
║      GDB Rust Function Tracer Loaded       ║
╠════════════════════════════════════════════╣
║ Commands:                                  ║
║   rust-trace [funcs]    : Trace functions  ║
║   rust-auto-trace       : Auto trace all   ║
║   rust-trace-stop       : Stop tracing     ║
║                                             ║
║ Options:                                   ║
║   --include-std         : Include std lib  ║
╚════════════════════════════════════════════╝
""")