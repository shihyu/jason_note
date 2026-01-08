#pragma once

#include <cstring>
#include <iostream>

// ============================================================================
// 編譯器優化巨集 (Compiler Optimization Macros)
// ============================================================================

// 分支預測提示 (Branch Prediction Hints)
// ⚡ 告訴編譯器該分支發生的機率，以優化 CPU 指令管線 (Pipeline)
// LIKELY(x): x 為真的機率很高 -> 編譯器將此分支代碼緊接在判斷指令後
// UNLIKELY(x): x 為真的機率很低 -> 編譯器將此分支代碼放到較遠的位置
#define LIKELY(x) __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

// 斷言檢查 (Assertion Check)
// 僅在條件失敗時執行錯誤處理 (UNLIKELY)
inline auto ASSERT(bool cond, const std::string& msg) noexcept
{
    if (UNLIKELY(!cond)) {
        std::cerr << "ASSERT : " << msg << std::endl;

        exit(EXIT_FAILURE);
    }
}

// 致命錯誤處理 (Fatal Error Handling)
inline auto FATAL(const std::string& msg) noexcept
{
    std::cerr << "FATAL : " << msg << std::endl;

    exit(EXIT_FAILURE);
}
