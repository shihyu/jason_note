# GDB trace script for zip compression
# This script automatically traces the zip compression process

set pagination off
set confirm off

# Set breakpoints at key functions
break main
break zip_zip
break mz_zip_writer_add_cfile

# Run the program
run

# At main()
echo \n=== Breakpoint: main() ===\n
info args
list
continue

# At zip_zip()
echo \n=== Breakpoint: zip_zip() ===\n
info args
backtrace 3
printf "Zip file: %s\n", czipfile
printf "Number of files: %d\n", num_files
printf "Compression level: %d\n", compression_level
list
continue

# At mz_zip_writer_add_cfile()
echo \n=== Breakpoint: mz_zip_writer_add_cfile() ===\n
info args
backtrace 3
printf "Archive key: %s\n", pArchive_name
printf "Uncompressed size: %llu bytes\n", (unsigned long long)size_to_add
list
continue

# Program completed
echo \n=== Program completed ===\n
quit
