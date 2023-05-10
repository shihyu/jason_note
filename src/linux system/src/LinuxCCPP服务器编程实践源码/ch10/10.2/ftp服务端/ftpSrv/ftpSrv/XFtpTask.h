#pragma once
#include <event2/bufferevent.h>

#include "XTask.h"

#include <string>
using namespace std;

struct bufferevent;

class XFtpTask :
    public XTask
{
public:
    string curDir = "/";
    string rootDir = ".";
    string ip = "";
    int port = 0;
    XFtpTask *cmdTask = 0;

    // 解析协议
    virtual void Parse(std::string, std::string) {}

    // 回复cmd消息
    void ResCMD(string msg);

    // 连接数据通道
    void ConnectoPORT();
    // 关闭连接
    void ClosePORT();

    // 通过数据通道发送数据
    void Send(const string& data);
    void Send(const char *data, size_t datasize);

    virtual void Event(bufferevent *, short) {}
    virtual void Read(bufferevent *) {}
    virtual void Write(bufferevent *) {}

    void Setcb(struct bufferevent*);
    bool Init() {
        return true;
    }

    ~XFtpTask();

protected:
    static void EventCB(bufferevent *, short, void *);
    static void ReadCB(bufferevent *, void *);
    static void WriteCB(bufferevent *, void *);

    // 在CMD中它是命令通道，在LIST和RETR中它是数据通道
    bufferevent *bev = 0;
    FILE *fp = 0;
};

