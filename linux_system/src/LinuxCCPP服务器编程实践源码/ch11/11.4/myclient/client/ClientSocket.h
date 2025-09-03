#pragma once

// CClientSocket ÃüÁîÄ¿±ê
#include "DlgChat.h"
class CClientSocket : public CSocket
{
public:
    CDlgChat *m_pDlg;
    void SetWnd(CDlgChat *pDlg);
    CClientSocket();
    virtual ~CClientSocket();
    virtual void OnReceive(int nErrorCode);
};


