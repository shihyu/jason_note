#pragma once
#include "XFtpTask.h"

#include <map>

class XFtpServerCMD : public XFtpTask
{
public:
    // ��ʼ������
    virtual bool Init();

    virtual void Event(bufferevent *be, short events);

    virtual void Read(bufferevent *be);

    // ע���������󣬲���Ҫ�����̰߳�ȫ������ʱδ�ַ����߳�
    void Reg(std::string, XFtpTask *call);


    XFtpServerCMD();
    ~XFtpServerCMD();
private:
    std::map<std::string, XFtpTask*>calls;
    std::map<XFtpTask*, int>calls_del;
};

