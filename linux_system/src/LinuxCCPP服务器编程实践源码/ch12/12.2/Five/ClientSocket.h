#pragma once

// CClientSocket ÃüÁîÄ¿±ê
#include "CDlgRoom.h"
class CClientSocket : public CSocket
{
public:
    CDlgRoom *m_pDlg;
    void SetWnd(CDlgRoom *pDlg);
    CClientSocket();
    virtual ~CClientSocket();
    virtual void OnReceive(int nErrorCode);
};


