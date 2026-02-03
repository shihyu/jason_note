# OpenEvolve 多語言演化（Assembly 範例整理）

## 多語言支援說明

OpenEvolve 支援多種程式語言的演化最佳化，可參考以下官方範例：

- **Rust｜自適應排序**  
  https://github.com/algorithmicsuperintelligence/openevolve/tree/main/examples/rust_adaptive_sort

- **R｜穩健回歸**  
  https://github.com/algorithmicsuperintelligence/openevolve/tree/main/examples/r_robust_regression

---

## Assembly（x86-64）演化設定重點

### 為什麼要用 Full Rewrite Mode？

- Assembly 使用 `;` 作為註解符號（不是 `#`）
- diff-based evolution 無法可靠處理 assembly
- **必須關閉 diff 模式，改為每次整份程式重寫**

---

## 設定檔（config.yaml）

```yaml
file_suffix: ".asm"   # 或 GNU assembler 使用 .s
diff_based_evolution: false  # Assembly 必須使用完整重寫模式

llm:
  system_message: |
    You are an expert in x86-64 assembly optimization.
    Rewrite the entire program to optimize for performance.
    Focus on:
    - Instruction-level parallelism (ILP)
    - Cache optimization
    - Register allocation
    - SIMD instructions
    - Modern CPU microarchitecture
      (out-of-order execution, branch prediction)
```

---

## 初始程式（initial_program.asm）

```asm
; 基礎 assembly routine（待優化）
section .text
global optimize_me
optimize_me:
    ; 初始實作
    ret
```

---

## 評測器（evaluator.py）

```python
# 使用 nasm / gas 組譯
subprocess.run(["nasm", "-f", "elf64", program_path, "-o", "output.o"])

# 與測試用 C 程式連結
subprocess.run(["gcc", "output.o", "test_harness.c", "-o", "benchmark"])

# 執行並量測效能指標
# - CPU cycles
# - Instructions
# - Cache misses
# - Throughput
```

---

## 應用場景（延伸）

- microbenchmark（如 memcpy / hash / sort kernel）
- HFT / 低延遲系統的 hot path
- CPU-specific hand-tuned assembly 自動化調校

> 這種做法本質上是一個「自動演化的 Assembly 效能調校器」
