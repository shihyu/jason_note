# zl_threadpool : 三個版本的線程池實現

[![Build Status](https://travis-ci.org/lizhenghn123/zl_threadpool.svg?branch=master)](https://api.travis-ci.org/lizhenghn123/zl_threadpool.svg?branch=master)

**Linux平臺下C++(C++98、C++03、C++11)實現的線程池**

- ThreadPoolCpp98

        最古老的做法，只使用了C++98語言規範，採用**面向對象的思路**，每一個任務都是一個子類對象；

- ThreadPoolCpp03
 
        較新做法，使用C++03語言規範，還有C++0x（特指std::function + std::bind），與上面不同的是採用
        **基於對象的思路**，每一個任務都是一個std::function對象，std::function，std::bind真是好；

- ThreadPoolCpp11

        最新做法，**完全採用C++11**技術，比如std::thread, mutex, condition_variable, atomic組件，
        還有lambda技巧，packaged_task， future等等；