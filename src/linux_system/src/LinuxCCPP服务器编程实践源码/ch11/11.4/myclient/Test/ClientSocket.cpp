// ClientSocket.cpp : ʵ���ļ�
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


// CClientSocket ��Ա����


void CClientSocket::OnReceive(int nErrorCode)
{
    // TODO:  �ڴ����ר�ô����/����û���
    char bufferdata[2048];
    int len = Receive(bufferdata, 2048);
    bufferdata[len] = '\0';
    theApp.m_ServerSock.SendAll(bufferdata, len);

    CSocket::OnReceive(nErrorCode);
}

