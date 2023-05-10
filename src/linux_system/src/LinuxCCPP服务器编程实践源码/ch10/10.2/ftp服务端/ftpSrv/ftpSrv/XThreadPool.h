#pragma once
#include <vector>

class XThread;
class XTask;
class XThreadPool
{
public:
    // ����ģʽ
    static XThreadPool *Get() {
        static XThreadPool p;
        return &p;
    }
    // ��ʼ�������߳�
    void Init(int threadCount);

    // �ַ��߳�
    void Dispatch(XTask*);
private:
    int threadCount;
    int lastThread = -1;
    std::vector<XThread *> threads;
    XThreadPool() {};
};

