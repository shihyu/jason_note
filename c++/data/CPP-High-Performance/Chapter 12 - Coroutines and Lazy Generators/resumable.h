// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：resumable.h

#pragma once

#include "chapter_12.h"

#ifdef SUPPORTS_COROUTINES

#include <exception>
#include <utility>

struct Resumable {
    struct promise_type;
    using handle_type = std::coroutine_handle<promise_type>;

    explicit Resumable(handle_type h) : h_(h) {}

    Resumable(Resumable&& other) noexcept : h_(std::exchange(other.h_, {})) {}
    Resumable& operator=(Resumable&& other) noexcept {
        if (this != &other) {
            if (h_) { h_.destroy(); }
            h_ = std::exchange(other.h_, {});
        }
        return *this;
    }

    ~Resumable() { if (h_) { h_.destroy(); } }

    bool resume() {
        if (!h_ || h_.done()) { return false; }
        h_.resume();
        return !h_.done();
    }

private:
    handle_type h_;
};

struct Resumable::promise_type {
    Resumable get_return_object() {
        return Resumable{handle_type::from_promise(*this)};
    }
    auto initial_suspend() { return std::suspend_always{}; }
    auto final_suspend() noexcept { return std::suspend_always{}; }
    void return_void() {}
    void unhandled_exception() { std::terminate(); }
};

#endif
