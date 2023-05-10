#pragma once
#include "XFtpTask.h"

#include <map>

class XFtpServerCMD : public XFtpTask
{
public:
    // 初始化任务
    virtual bool Init();

    virtual void Event(bufferevent *be, short events);

    virtual void Read(bufferevent *be);

    // 注册命令处理对象，不需要考虑线程安全，调用时未分发到线程
    void Reg(std::string, XFtpTask *call);


    XFtpServerCMD();
    ~XFtpServerCMD();
private:
    std::map<std::string, XFtpTask*>calls;
    std::map<XFtpTask*, int>calls_del;
};

