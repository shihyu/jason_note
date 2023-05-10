#include <thread>
#include <iostream>
using namespace std;

#include <unistd.h>

#include <event2/event.h>

#include "testUtil.h"
#include "XThread.h"
#include "XTask.h"



/*
 *  线程监听主线程对自己的通知
 */
static void Notify_cb(evutil_socket_t fd, short which, void *arg) {
    XThread *t = (XThread*)arg;
    t->Notify(fd, which);
}

void XThread::Notify(evutil_socket_t fd, short which) {
    testout(id << " thread At Notify()");
    char buf[2] = { 0 };

    int re = read(fd, buf, 1);
    if (re < 0)
        return;
    cout << id << " thread recv" << buf << endl;
}


/*
 *  启动线程
 */
void XThread::Start() {
    testout(id << " thread At Start()");
    Setup();
    thread th(&XThread::Main, this);
    th.detach();
}

/*
 *  线程流持续处理任务的地方
 */
void XThread::Main() {
    cout << id << " thread::Main() begin" << endl;
    event_base_dispatch(base);
    event_base_free(base);
    cout << id << " thread::Main() end" << endl;
}

/*
 *  安装线程
 */
bool XThread::Setup() {
    testout(id << " thread At Setup");

    int fds[2];

    if (pipe(fds)) {
        cerr << "pipe failed" << endl;
        return false;
    }

    // 用于主线程通知子线程处理任务，windows用配对socket，linux用管道
    notify_send_fd = fds[1];

    // 创建lievent上下文
    event_config *ev_conf = event_config_new();
    event_config_set_flag(ev_conf, EVENT_BASE_FLAG_NOLOCK);
    this->base = event_base_new_with_config(ev_conf);
    event_config_free(ev_conf);
    if (!base) {
        cout << "event_base_new_with_config error!" << endl;
        return false;
    }

    // 添加管道监听事件，用于线程池激活自己执行任务, 将this传入
    event *ev = event_new(base, fds[0], EV_READ | EV_PERSIST, Notify_cb, this);
    event_add(ev, 0);

    return true;
}

/*
 *  激活线程
 */
void XThread::Activate() {
    testout(id << " thread At Activate()");


    int re = write(notify_send_fd, "c", 1);

    if (re <= 0) {
        cerr << "XThread::Activate() fail" << endl;
    }
    // 获取任务，并初始化
    XTask *t = NULL;
    tasks_mutex.lock();
    if (tasks.empty()) {
        tasks_mutex.unlock();
        return;
    }
    t = tasks.front();
    tasks.pop_front();
    tasks_mutex.unlock();
    t->Init();
}

/*
 *  添加任务
 */
void XThread::AddTack(XTask *t) {
    if (!t) return;

    // 任务继承线程的libevent上下文，命令处理任务在这个上下文注册事件，使线程处理任务添加的事件
    t->base = this->base;

    tasks_mutex.lock();
    tasks.push_back(t);
    tasks_mutex.unlock();
}

XThread::XThread() {

}
XThread::~XThread() {

}
