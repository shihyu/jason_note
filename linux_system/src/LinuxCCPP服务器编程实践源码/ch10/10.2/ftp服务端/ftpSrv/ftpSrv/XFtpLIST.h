#pragma once
#include "XFtpTask.h"
#include <string>
using namespace std;
class XFtpLIST : public XFtpTask
{
public:
    virtual void Parse(std::string, std::string);
    virtual void Event(bufferevent *, short);
    virtual void Write(bufferevent *);

private:
    string GetListData(string path);
};

