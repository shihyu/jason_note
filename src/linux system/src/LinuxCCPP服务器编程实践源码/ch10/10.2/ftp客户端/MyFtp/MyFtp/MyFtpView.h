//created by zww
// MyFtpView.h : interface of the CMyFtpView class
//
/////////////////////////////////////////////////////////////////////////////

#if !defined(AFX_MYFTPVIEW_H__590C5A0C_F3EA_4ADA_AD00_C3D694EDD975__INCLUDED_)
#define AFX_MYFTPVIEW_H__590C5A0C_F3EA_4ADA_AD00_C3D694EDD975__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "ConnectDlg.h"
#include "FtpDlg.h"

class CMyFtpView : public CView
{
protected: // create from serialization only
    CMyFtpView();
    DECLARE_DYNCREATE(CMyFtpView)

//myData
public:
    CConnectDlg m_ConDlg;
    CFtpDlg     m_FtpDlg;
    CString m_FtpWebSite;
    CString m_UserName;
    CString m_UserPwd;

    CInternetSession* m_pSession;
    CFtpConnection* m_pConnection;
    CFtpFileFind* m_pFileFind;
// Attributes
public:
    CMyFtpDoc* GetDocument();

// Operations
public:

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CMyFtpView)
public:
    virtual void OnDraw(CDC* pDC);  // overridden to draw this view
    virtual BOOL PreCreateWindow(CREATESTRUCT& cs);
protected:
    virtual BOOL OnPreparePrinting(CPrintInfo* pInfo);
    virtual void OnBeginPrinting(CDC* pDC, CPrintInfo* pInfo);
    virtual void OnEndPrinting(CDC* pDC, CPrintInfo* pInfo);
    //}}AFX_VIRTUAL

// Implementation
public:
    virtual ~CMyFtpView();
#ifdef _DEBUG
    virtual void AssertValid() const;
    virtual void Dump(CDumpContext& dc) const;
#endif

protected:

// Generated message map functions
protected:
    //{{AFX_MSG(CMyFtpView)
    afx_msg BOOL OnEraseBkgnd(CDC* pDC);
    afx_msg void OnConnect();
    afx_msg void OnTimer(UINT nIDEvent);
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
public:
    virtual void OnInitialUpdate();
};

#ifndef _DEBUG  // debug version in MyFtpView.cpp
inline CMyFtpDoc* CMyFtpView::GetDocument()
{
    return (CMyFtpDoc*)m_pDocument;
}
#endif

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MYFTPVIEW_H__590C5A0C_F3EA_4ADA_AD00_C3D694EDD975__INCLUDED_)
