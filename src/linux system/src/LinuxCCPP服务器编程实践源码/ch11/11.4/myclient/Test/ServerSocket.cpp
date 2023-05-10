// ServerSocket.cpp : ʵ���ļ�
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


// CServerSocket ��Ա����



void CServerSocket::OnAccept(int nErrorCode)
{
    // TODO:  �ڴ����ר�ô����/����û���
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