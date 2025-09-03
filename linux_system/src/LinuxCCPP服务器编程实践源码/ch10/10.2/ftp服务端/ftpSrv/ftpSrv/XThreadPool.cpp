#include "XThreadPool.h"
#include "XThread.h"
#include "XTask.h"
#include <thread>
#include <iostream>
using namespace std;

#include "testUtil.h"

/*
 *  分配任务到线程池
 */
void XThreadPool::Dispatch(XTask *task) {
    testout("main thread At XThreadPoll::dispathch()");

    if (!task) return;
    int tid = (lastThread + 1) % threadCount;
    lastThread = tid;
    XThread *t = threads[tid];

    // 添加任务
    t->AddTack(task);
    // 激活线程
    t->Activate();
}

/*
 *  初始化线程池
 */
void XThreadPool::Init(int threadCount) {
    testout("main thread At XThreadPoll::Init()");
    this->threadCount = threadCount;
    this->lastThread = -1;
    for (int i = 0; i < threadCount; i++) {
        cout << "Create thread" << i << endl;
        XThread *t = new XThread();
        t->id = i;
        t->Start();
        threads.push_back(t);
        this_thread::sleep_for(chrono::milliseconds(10));
    }

}
