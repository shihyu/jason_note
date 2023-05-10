//zww
// Five.h : main header file for the FIVE application
//


#if !defined(AFX_FIVE_H__C6EF525F_4D94_4C1A_B242_7FA2ED813893__INCLUDED_)
#define AFX_FIVE_H__C6EF525F_4D94_4C1A_B242_7FA2ED813893__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
#error include 'stdafx.h' before including this file for PCH
#endif

#include "ClientSocket.h"
#include "resource.h"		// main symbols
#include "CDlgLogin.h"
/////////////////////////////////////////////////////////////////////////////
// CFiveApp:
// See Five.cpp for the implementation of this class
//


class CFiveApp : public CWinApp
{
public:
    //m_szCreatorIPAsJoin������Ϊ��������ߣ������Ĵ����ߵ�IP��m_szMyIPAsCreator������Ϊ���������ߵ�IP����IP�Ժ�Ҫ�ڴ����﹫ʾ��
    char m_szCreatorIPAsJoin[100],m_szMyIPAsCreator[100];
    int m_isCreator;
    CDlgLogin *m_pDlgLogin;
    CString m_strName;//��ǰ��¼���������˵��û���
    CClientSocket m_clinetsock;
    TCHAR m_szIni[MAX_PATH];
    int m_nWin;
    int m_nDraw;
    int m_nLost;
    CFiveApp();

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CFiveApp)
public:
    virtual BOOL InitInstance();
    //}}AFX_VIRTUAL

// Implementation

    //{{AFX_MSG(CFiveApp)
    // NOTE - the ClassWizard will add and remove member functions here.
    //    DO NOT EDIT what you see in these blocks of generated code !
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_FIVE_H__C6EF525F_4D94_4C1A_B242_7FA2ED813893__INCLUDED_)
