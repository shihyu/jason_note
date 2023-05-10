#include "XFtpLIST.h"
#include "event2/bufferevent.h"
#include "event2/event.h"
#include "testUtil.h"
#include <string>
using namespace std;




void XFtpLIST::Write(bufferevent *bev) {
    testout("XFtpLIST::Write");
    ResCMD("226 Transfer comlete");
    ClosePORT();
}

void XFtpLIST::Event(bufferevent *bev, short events) {
    testout("At XFtpLIST::Event");
    if (events & (BEV_EVENT_EOF | BEV_EVENT_ERROR | BEV_EVENT_TIMEOUT)) {
        ClosePORT();
    }
    else if (events & BEV_EVENT_CONNECTED)
        cout << "XFtpLIST BEV_EVENT_CONNECTED" << endl;
}

void XFtpLIST::Parse(std::string type, std::string msg) {
    testout("At XFtpLIST::Parse");
    string resmsg = "";
    if (type == "PWD") {
        // 257 "/" is current directory.
        resmsg = "257 \"";
        resmsg += cmdTask->curDir;
        resmsg += "\" is current dir.";
        ResCMD(resmsg);
    }
    else if (type == "LIST") {
        // 1 ����150����ظ�
        // 2 ��������ͨ����ͨ������ͨ����������
        // 3 ����226����ظ����
        // 4 �ر�����
        // ����ͨ���ظ���Ϣ ʹ������ͨ������Ŀ¼
        //  "-rwxrwxrwx 1 root root      418 Mar 21 16:10 XFtpFactory.cpp";
        string path = cmdTask->rootDir + cmdTask->curDir;
        testout("listpath: " << path);
        string listdata = GetListData(path);
        ConnectoPORT();
        ResCMD("150 Here coms the directory listing.");
        Send(listdata);
    }
    else if (type == "CWD") //�л�Ŀ¼
    {
        //ȡ�������е�·��
        //CWD test\r\n
        int pos = msg.rfind(" ") + 1;
        //ȥ����β��\r\n
        string path = msg.substr(pos, msg.size() - pos - 2);
        if (path[0] == '/') //�ֶ�·��
        {
            cmdTask->curDir = path;
        }
        else
        {
            if (cmdTask->curDir[cmdTask->curDir.size() - 1] != '/')
                cmdTask->curDir += "/";
            cmdTask->curDir += path + "/";
        }
        if (cmdTask->curDir[cmdTask->curDir.size() - 1] != '/')
            cmdTask->curDir += "/";
        //  /test/
        ResCMD("250 Directory succes chanaged.\r\n");

        //cmdTask->curDir +=
    }
    else if (type == "CDUP") //�ص��ϲ�Ŀ¼
    {
        if (msg[4] == '\r') {
            cmdTask->curDir = "/";
        }
        else {
            //  /Debug/test_ser.A3C61E95.tlog /Debug   /Debug/
            string path = cmdTask->curDir;
            //ͳһȥ����β�� /
            ////  /Debug/test_ser.A3C61E95.tlog /Debug
            if (path[path.size() - 1] == '/')
            {
                path = path.substr(0, path.size() - 1);
            }
            int pos = path.rfind("/");
            path = path.substr(0, pos);
            cmdTask->curDir = path;
            if (cmdTask->curDir[cmdTask->curDir.size() - 1] != '/')
                cmdTask->curDir += "/";
        }
        ResCMD("250 Directory succes chanaged.\r\n");
    }
}

string XFtpLIST::GetListData(string path) {
    // -rwxrwxrwx 1 root root 418 Mar 21 16:10 XFtpFactory.cpp

    string data = "";
    string cmd = "ls -l ";
    cmd += path;
    FILE *f = popen(cmd.c_str(), "r");
    if (!f) return data;
    char buf[1024] = {0};
    while (1) {
        int len = fread(buf, 1, sizeof(buf) - 1, f);
        if (len <= 0)break;
        buf[len] = '\0';
        data += buf;
    }
    pclose(f);

    return data;
}
