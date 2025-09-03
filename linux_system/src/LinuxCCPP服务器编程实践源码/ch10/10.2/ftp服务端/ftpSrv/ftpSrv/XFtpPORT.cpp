#include "XFtpPORT.h"
#include "testUtil.h"

#include <iostream>
#include <vector>
using namespace std;


void XFtpPORT::Parse(string type, string msg) {
    testout("XFtpPORT::Parse");
    // PORT 127,0,0,1,70,96\r\n
    // PORT n1,n2,n3,n4,n5,n6\r\n
    // port = n5 * 256 + n6

    vector<string>vals;
    string tmp = "";
    for (int i = 5; i < msg.size(); i++) {
        if (msg[i] == ',' || msg[i] == '\r') {
            vals.push_back(tmp);
            tmp = "";
            continue;
        }
        tmp += msg[i];
    }
    if (vals.size() != 6) {
        ResCMD("501 Syntax error in parameters or arguments.");
        return;
    }

    // 解析出ip和port，并设置在主要流程cmdTask下
    ip = vals[0] + "." + vals[1] + "." + vals[2] + "." + vals[3];
    port = atoi(vals[4].c_str()) * 256 + atoi(vals[5].c_str());
    cmdTask->ip = ip;
    cmdTask->port = port;
    testout("ip: " << ip);
    testout("port: " << port);
    ResCMD("200 PORT command success.");
}
