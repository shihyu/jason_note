//created by zww
// MyFtp.h : main header file for the MYFTP application
//

#if !defined(AFX_MYFTP_H__97FFA270_7968_440D_BFA3_2E67A4D21075__INCLUDED_)
#define AFX_MYFTP_H__97FFA270_7968_440D_BFA3_2E67A4D21075__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"       // main symbols

/////////////////////////////////////////////////////////////////////////////
// CMyFtpApp:
// See MyFtp.cpp for the implementation of this class
//

class CMyFtpApp : public CWinApp
{
public:
    CMyFtpApp();

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CMyFtpApp)
public:
    virtual BOOL InitInstance();
    //}}AFX_VIRTUAL

// Implementation
    //{{AFX_MSG(CMyFtpApp)
    afx_msg void OnAppAbout();
    // NOTE - the ClassWizard will add and remove member functions here.
    //    DO NOT EDIT what you see in these blocks of generated code !
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MYFTP_H__97FFA270_7968_440D_BFA3_2E67A4D21075__INCLUDED_)
