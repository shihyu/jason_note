// 高效能關鍵技術示例
// 關鍵技術：計數信號量控制併發資源。
// 章節：Concurrency - 檔案：counting_semaphore.cpp

#include <semaphore>
#include <thread>
#include <iostream>

class Request { };

class Server {
public:
    // Server() : sem_(4) { }
    
    void handle(const Request &req)
    {
        sem_.acquire();
        do_handle(req);
        sem_.release();
    }
    
private:
    // 關鍵技術：計數信號量控制併發資源。
    std::counting_semaphore<4> sem_{4};
    // or
    // std::counting_semaphore<4> sem_ = std::counting_semaphore<4>(4);
    // or
    // std::counting_semaphore<4> sem_; + constructor
    
    void do_handle(const Request &req) { std::cout << "woofwoof\n"; }
};

int main()
{
    Server().handle(Request());
  
    return 0;
}
