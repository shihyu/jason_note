// ClientSocket.cpp : 实现文件
//

#include "stdafx.h"
#include "Test.h"
#include "ClientSocket.h"


// CClientSocket

CClientSocket::CClientSocket()
{
}

CClientSocket::~CClientSocket()
{
}


// CClientSocket 成员函数


void CClientSocket::OnReceive(int nErrorCode)
{
    // TODO:  在此添加专用代码和/或调用基类
    char bufferdata[2048];
    int len = Receive(bufferdata, 2048);
    bufferdata[len] = '\0';
    theApp.m_ServerSock.SendAll(bufferdata, len);

    CSocket::OnReceive(nErrorCode);
}

