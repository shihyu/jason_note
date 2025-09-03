#pragma once

// CClientSocket ÃüÁîÄ¿±ê
class CClientSocket : public CSocket
{
public:
    CClientSocket();
    virtual ~CClientSocket();
    virtual void OnReceive(int nErrorCode);
};


