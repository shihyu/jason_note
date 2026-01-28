// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：include_check.h

// ORIGINAL SOURCE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// https://github.com/PacktPublishing/Cpp-High-Performance-Second-Edition/blob/df6dde71705bc474447c4d2f727b97d728d615c8/Chapter12/chapter_12.h
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#pragma once 

#include <version>

#if defined(__cpp_impl_coroutine) && defined(__cpp_lib_coroutine)
#include <coroutine>
#define SUPPORTS_COROUTINES
#endif 


#if !defined(SUPPORT_COROUTINES) && defined(__has_include)

#if __has_include(<coroutine>)

#include <coroutine>
#define SUPPORTS_COROUTINES

#elif __has_include(<experimental/coroutine>) // Check for an experimental version

#include <experimental/coroutine>
// 關鍵技術：協程與 lazy generator。
namespace std {
    // 關鍵技術：協程與 lazy generator。
    using std::experimental::coroutine_handle;
    using std::experimental::suspend_always;
    using std::experimental::suspend_never;
}
#define SUPPORTS_COROUTINES

#endif

#endif // __has_include
