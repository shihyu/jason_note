#pragma once
#include <event2/util.h>
#include <list>
#include <mutex>
class XTask;
struct event_base;
class XThread
{
public:
    // 启动线程
    void Start();

    // 线程入口函数
    void Main();

    // 安装线程，初始化evevnt_base和管道监听事件用于激活
    bool Setup();

    // 收到主线程发出的激活消息（线程池任务分发）
    void Notify(evutil_socket_t, short);

    // 线程激活
    void Activate();

    // 添加任务, 一个线程可以同时处理多个任务，共用一个event_base
    void AddTack(XTask *);

    XThread();
    ~XThread();

    // 线程编号
    int id = 0;

private:
    int notify_send_fd = 0;
    event_base *base = 0;
    std::list<XTask*> tasks;
    std::mutex tasks_mutex;
};

