// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：chapter_12.h

#pragma once

#if defined(__has_include)
#if __has_include(<coroutine>)
#include <coroutine>
#define SUPPORTS_COROUTINES
#elif __has_include(<experimental/coroutine>)
#include <experimental/coroutine>
namespace std {
    using std::experimental::coroutine_handle;
    using std::experimental::suspend_always;
    using std::experimental::suspend_never;
}
#define SUPPORTS_COROUTINES
#endif
#endif
