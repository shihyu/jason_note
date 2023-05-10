#pragma once

// CServerSocket ÃüÁîÄ¿±ê


class CServerSocket : public CSocket
{
public:
    void CServerSocket::DelAll();
    void SendAll(char *bufferdata, int len);
    CPtrList  m_socketlist;
    CServerSocket();
    virtual ~CServerSocket();
    virtual void OnAccept(int nErrorCode);
};


