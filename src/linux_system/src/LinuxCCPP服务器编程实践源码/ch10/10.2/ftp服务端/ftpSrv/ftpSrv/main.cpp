#include <iostream>
using std::cout;
using std::cin;
using std::endl;
using std::cerr;
using std::flush;
#include <event2/event.h>
#include <stdlib.h>

#include <signal.h>

#define errmsg(msg) do{cout<< msg << endl;exit(1);}while(0)
/**************basic include***************/
#include <string.h>
#include <string>
using std::string;
#include <fstream>

#include <event2/listener.h>
#include <event2/bufferevent.h>
#include <event2/http.h>
#include <event2/keyvalq_struct.h>
#include <event2/buffer.h>
#include <event2/util.h>

#include "testUtil.h"
#include "XThreadPool.h"
#include "XThread.h"
#include "XTask.h"
#include "XFtpFactory.h"


#define SPORT 21
#define BUFS 1024

#define XThreadPoolGet XThreadPool::Get()

/*
 *  接待连接的回调函数
 */
void listen_cb(struct evconnlistener *ev, evutil_socket_t s, struct sockaddr *addr, int socklen, void *arg) {
    testout("main thread At listen_cb");
    sockaddr_in *sin = (sockaddr_in*)addr;
    /*
     *  创建任务
     */
    XTask *task = XFtpFactory::Get()->CreateTask();
    task->sock = s;
    /*
     *  分配任务
     */
    XThreadPoolGet->Dispatch(task);
}

int main() {


    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR)
        errmsg("signal(SIGPIPE, SIG_IGN) error!");


    /*
     *  初始化线程池
     */
    XThreadPoolGet->Init(10);

    event_base *base = event_base_new();
    if (!base)
        errmsg("main thread event_base_new error");

    /*
     *  创建libevent上下文
     */
    sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(SPORT);

    /*
     *  创建监听事件
     */
    evconnlistener *ev = evconnlistener_new_bind(
                             base,											// libevent的上下文
                             listen_cb,										//接收到连接的回调函数
                             base,											//回调函数获取的参数 arg
                             LEV_OPT_REUSEABLE|LEV_OPT_CLOSE_ON_FREE,		//地址重用，evconnlistener关闭同时关闭socket
                             10,												//连接队列大小，对应listen函数
                             (sockaddr*)&sin,								//绑定的地址和端口
                             sizeof(sin));

    if (base) {
        cout << "begin to listen..." << endl;
        event_base_dispatch(base);
    }
    if (ev)
        evconnlistener_free(ev);
    if (base)
        event_base_free(base);
    testout("server end");
    return 0;
}

