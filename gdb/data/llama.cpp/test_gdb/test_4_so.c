#include <stdio.h>
#include "../ggml/include/ggml.h"
#include "../include/llama.h"

int main() {
    printf("測試 4 個 .so 檔案\n\n");

    // 1. libggml.so
    printf("[1] libggml.so - ggml_backend_load_all()\n");
    ggml_backend_load_all();

    // 2. libllama.so
    printf("[2] libllama.so - llama_model_default_params()\n");
    struct llama_model_params mp = llama_model_default_params();

    // 3. libggml-base.so
    printf("[3] libggml-base.so - ggml_init()\n");
    struct ggml_init_params params = {.mem_size = 1024*1024, .mem_buffer = NULL};
    struct ggml_context *ctx = ggml_init(params);

    // 4. libggml-cpu.so
    printf("[4] libggml-cpu.so - ggml_backend_cpu_init()\n");
    ggml_backend_t cpu_backend = ggml_backend_cpu_init();

    printf("\n完成! 4 個 .so 都已測試\n");

    if (cpu_backend) ggml_backend_free(cpu_backend);
    ggml_free(ctx);
    return 0;
}
