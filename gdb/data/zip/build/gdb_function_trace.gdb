# Function tracing script - shows execution path with file:line info
# Reads breakpoints from breakpoints.gdb and auto-continues

set pagination off
set confirm off

# Load breakpoints from file and set auto-continue
source breakpoints.gdb

# Set commands for all breakpoints to show location and continue
commands 1-999
  silent
  where 1
  continue
end

echo === Function Trace Started ===\n

# Run the program
run

# Program completed
echo \n=== Function Trace Completed ===\n
quit
