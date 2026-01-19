# Chapter 11 - Concurrency

重點摘要
- 執行緒生命週期與 join/jthread 的管理。
- 同步原語：mutex、condition_variable、semaphore、latch、barrier。
- atomic/atomic_ref 與 false sharing 風險。
- lock-free 結構與 bounded buffer。
- promise/future/async 的非同步模式。

關鍵程式碼
- async.cpp
```cpp
        // 關鍵技術：非同步任務與結果傳遞。
        std::cout << "Result: " << std::async(divide, 45, 5).get() << '\n';
    } catch (const std::exception &e) {
        std::cout << "Exception caught: " << e.what() << '\n';
    }
```

程式碼清單
- async.cpp
- atomic_ref.cpp
- atomic_shared_ptr.cpp
- barriers.cpp
- bm_threads.cpp
- bounded_buffer_1.cpp
- bounded_buffer_2.cpp
- coin_flips.cpp
- coin_game.cpp
- condition_variables.cpp
- counting_semaphore.cpp
- false_sharing.cpp
- join.cpp
- jthread.cpp
- latch_example.cpp
- lock_free_queue.cpp
- money_transfer.cpp
- not_so_atomic_ref.cpp
- promises.cpp
- task.cpp
- wait_overload.cpp
