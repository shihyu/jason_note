#!/bin/bash
# run_all_traces.sh - 整合執行所有追蹤方法

echo "========================================="
echo "Program Flow Tracing Tool"
echo "========================================="

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <source_file>"
    echo "Example: $0 test_program.cpp"
    echo "         $0 test_program.rs"
    exit 1
fi

SOURCE_FILE=$1
FILE_EXT="${SOURCE_FILE##*.}"
BASE_NAME="${SOURCE_FILE%.*}"

# 檢查源檔案是否存在
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '$SOURCE_FILE' not found"
    exit 1
fi

# 編譯程式
echo "Compiling $SOURCE_FILE..."
case $FILE_EXT in
    cpp|cc|cxx)
        g++ -g -O0 -pg $SOURCE_FILE -o $BASE_NAME
        if [ $? -ne 0 ]; then
            echo "Compilation failed"
            exit 1
        fi
        ;;
    c)
        gcc -g -O0 -pg $SOURCE_FILE -o $BASE_NAME
        if [ $? -ne 0 ]; then
            echo "Compilation failed"
            exit 1
        fi
        ;;
    rs)
        rustc -g $SOURCE_FILE -o $BASE_NAME
        if [ $? -ne 0 ]; then
            echo "Compilation failed"
            exit 1
        fi
        ;;
    *)
        # 如果不是源碼檔案，假設是已編譯的執行檔
        if [ -x "$SOURCE_FILE" ]; then
            BASE_NAME=$SOURCE_FILE
            FILE_EXT="exe"
        else
            echo "Unsupported file type: $FILE_EXT"
            exit 1
        fi
        ;;
esac

echo "Compilation successful: $BASE_NAME"

# 方法 1: GDB
echo -e "\n[1] Running GDB trace..."
if [ -f "./gdb_trace.sh" ]; then
    ./gdb_trace.sh $BASE_NAME
    if [ -f "gdb_to_graph.py" ]; then
        python3 gdb_to_graph.py
    fi
else
    echo "Warning: gdb_trace.sh not found"
fi

# 方法 2: uftrace (C/C++ only)
if [[ $FILE_EXT != "rs" ]]; then
    echo -e "\n[2] Running uftrace..."
    if [ -f "./uftrace_trace.sh" ]; then
        ./uftrace_trace.sh $SOURCE_FILE
        if [ -f "uftrace_to_graph.py" ]; then
            python3 uftrace_to_graph.py
        fi
    else
        echo "Warning: uftrace_trace.sh not found"
    fi
else
    echo -e "\n[2] uftrace not fully supported for Rust"
fi

# 產生火焰圖 (if available)
if [ -f flame.txt ]; then
    echo -e "\n[3] Generating FlameGraph..."
    if [ ! -d FlameGraph ]; then
        echo "FlameGraph tools not found. Clone from:"
        echo "git clone https://github.com/brendangregg/FlameGraph"
    else
        cat flame.txt | ./FlameGraph/flamegraph.pl > flamegraph.svg
        echo "FlameGraph saved to flamegraph.svg"
    fi
fi

# 建立輸出目錄並整理檔案
echo -e "\n[4] Organizing output files..."
mkdir -p graphs
mkdir -p logs

# 移動圖表檔案
for file in *.svg *.png; do
    if [ -f "$file" ]; then
        mv "$file" graphs/ 2>/dev/null
    fi
done

# 移動日誌檔案
for file in gdb_trace.log uftrace_trace.txt trace.json flame.txt; do
    if [ -f "$file" ]; then
        mv "$file" logs/ 2>/dev/null
    fi
done

echo -e "\n========================================="
echo "Completed! Generated files:"
echo "Graphs: $(ls -1 graphs/ 2>/dev/null | wc -l) files"
ls -la graphs/*.svg graphs/*.png 2>/dev/null | grep -E "\.(svg|png)$"
echo ""
echo "Logs: $(ls -1 logs/ 2>/dev/null | wc -l) files"
ls -la logs/ 2>/dev/null | tail -n +2 | grep -v "^total"
echo "========================================="

# 提示如何查看結果
echo -e "\nTo view the graphs:"
echo "  Open graphs/gdb_flow.svg in a browser"
echo "  Open graphs/uftrace_flow.svg in a browser"
echo ""
echo "To view Chrome trace:"
echo "  1. Open Chrome browser"
echo "  2. Navigate to chrome://tracing"
echo "  3. Load logs/trace.json"