#pragma once

// CClientSocket ����Ŀ��
class CClientSocket : public CSocket
{
public:
    CClientSocket();
    virtual ~CClientSocket();
    virtual void OnReceive(int nErrorCode);
};


