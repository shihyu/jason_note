// ServerSocket.cpp : 实现文件
//

#include "stdafx.h"
#include "Test.h"
#include "ServerSocket.h"
#include "ClientSocket.h"

// CServerSocket

CServerSocket::CServerSocket()
{
}

CServerSocket::~CServerSocket()
{
}


// CServerSocket 成员函数



void CServerSocket::OnAccept(int nErrorCode)
{
    // TODO:  在此添加专用代码和/或调用基类
    CClientSocket* psocket = new CClientSocket();
    if (Accept(*psocket))
        m_socketlist.AddTail(psocket);
    else
        delete psocket;

    CSocket::OnAccept(nErrorCode);

}



void CServerSocket::SendAll(char *bufferdata, int len)
{
    if (len != -1)
    {
        bufferdata[len] = 0;
        POSITION pos = m_socketlist.GetHeadPosition();
        while (pos != NULL)
        {
            CClientSocket* socket = (CClientSocket*)m_socketlist.GetNext(pos);
            if (socket != NULL)
                socket->Send(bufferdata, len);
        }
    }
}


void CServerSocket::DelAll()
{
    POSITION pos = m_socketlist.GetHeadPosition();
    while (pos != NULL)
    {
        CClientSocket* socket = (CClientSocket*)m_socketlist.GetNext(pos);
        if (socket != NULL)
            delete socket;
    }
    m_socketlist.RemoveAll();
}