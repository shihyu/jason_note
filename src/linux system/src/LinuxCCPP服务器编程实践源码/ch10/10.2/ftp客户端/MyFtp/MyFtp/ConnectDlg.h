//created by zww
#if !defined(AFX_CONNECTDLG_H__ED552260_9B20_4618_85F7_E15762412198__INCLUDED_)
#define AFX_CONNECTDLG_H__ED552260_9B20_4618_85F7_E15762412198__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ConnectDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CConnectDlg dialog

class CConnectDlg : public CDialog
{
// Construction
public:
    CConnectDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
    //{{AFX_DATA(CConnectDlg)
    enum { IDD = IDD_DIALOG1 };
    CString	m_FtpWebSite;
    CString	m_UserName;
    CString	m_UserPwd;
    //}}AFX_DATA


// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CConnectDlg)
protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
    //}}AFX_VIRTUAL

// Implementation
protected:

    // Generated message map functions
    //{{AFX_MSG(CConnectDlg)
    afx_msg void OnConnect();
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CONNECTDLG_H__ED552260_9B20_4618_85F7_E15762412198__INCLUDED_)
