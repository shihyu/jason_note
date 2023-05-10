#pragma once
#include "XFtpTask.h"
class XFtpRETR :
    public XFtpTask
{
    void Parse(std::string type, std::string msg);
    virtual void Event(bufferevent *, short);
    virtual void Write(bufferevent *);

    bool Init() {
        return true;
    }


private:
    char buf[1024*1024] = {0};
};

