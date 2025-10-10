#!/bin/bash

export LD_LIBRARY_PATH=../build/bin:$LD_LIBRARY_PATH

echo "========================================"
echo "  測試 4 個 .so 檔案的 gdb 中斷"
echo "========================================"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo ""

gdb -batch \
  -ex "file ./test_4_so" \
  -ex "break ggml_backend_load_all" \
  -ex "break llama_model_default_params" \
  -ex "break ggml_init" \
  -ex "break ggml_backend_cpu_init" \
  -ex "run" \
  -ex "echo \n✓ [1/4] libggml.so\n" \
  -ex "backtrace 2" \
  -ex "continue" \
  -ex "echo \n✓ [2/4] libllama.so\n" \
  -ex "backtrace 2" \
  -ex "continue" \
  -ex "echo \n✓ [3/4] libggml-base.so\n" \
  -ex "backtrace 2" \
  -ex "continue" \
  -ex "echo \n✓ [4/4] libggml-cpu.so\n" \
  -ex "backtrace 2" \
  -ex "info sharedlibrary" \
  -ex "continue"
