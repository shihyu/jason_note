#pragma once
#include "XFtpTask.h"
#include <string>
using namespace std;

class XFtpPORT : public XFtpTask
{
public:
    void Parse(string type, string msg);
};

