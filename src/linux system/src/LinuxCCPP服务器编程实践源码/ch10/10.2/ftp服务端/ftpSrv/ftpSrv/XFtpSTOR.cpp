#include "XFtpSTOR.h"
#include "testUtil.h"
#include <event2/bufferevent.h>
#include <event2/event.h>
#include <iostream>
#include <string>
using namespace std;

void XFtpSTOR::Read(bufferevent *bev) {
    testout("At XFtpSTOR::Read");
    if (!fp) return;
    while (1) {
        int len = bufferevent_read(bev, buf, sizeof(buf));
        if (len <= 0) {
            return;
        }
        fwrite(buf, 1, len, fp);
    }
}

void XFtpSTOR::Event(bufferevent *bev, short events) {
    testout("At XFtpSTOR::Event");
    if (events & (BEV_EVENT_EOF | BEV_EVENT_ERROR | BEV_EVENT_TIMEOUT)) {
        ClosePORT();
        ResCMD("226 Transfer complete");
    }
    else if (events & BEV_EVENT_CONNECTED)
        cout << "XFtpSTOR BEV_EVENT_CONNECTED" << endl;
}

void XFtpSTOR::Parse(std::string type, std::string msg) {
    testout("At XFtpSTOR::Parse");
    int pos = msg.rfind(" ") + 1;
    string filename = msg.substr(pos, msg.size() - pos - 2);
    string path = cmdTask->rootDir + cmdTask->curDir + filename;
    testout("filepath:[" << path << "]");
    fp = fopen(path.c_str(), "wb");
    if (fp) {
        ConnectoPORT();
        ResCMD("125 File OK");
        bufferevent_trigger(bev, EV_READ, 0);
    }
    else {
        ResCMD("450 file open failed!");
    }

}

