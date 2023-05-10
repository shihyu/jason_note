//zww
#if !defined(AFX_SERVERDLG_H__E6F20C03_AA02_44B8_8E15_FF084269166A__INCLUDED_)
#define AFX_SERVERDLG_H__E6F20C03_AA02_44B8_8E15_FF084269166A__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ServerDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CServerDlg dialog

class CServerDlg : public CDialog
{
// Construction
public:
    CServerDlg(CWnd* pParent = NULL);   // standard constructor
    void startGame();
// Dialog Data
    //{{AFX_DATA(CServerDlg)
    enum { IDD = IDD_DLG_SERVER };
    // NOTE: the ClassWizard will add data members here
    //}}AFX_DATA


// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CServerDlg)
protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
    //}}AFX_VIRTUAL

// Implementation
protected:

    // Generated message map functions
    //{{AFX_MSG(CServerDlg)
    virtual BOOL OnInitDialog();
    afx_msg void OnBtnLeave();
    virtual void OnCancel();
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_SERVERDLG_H__E6F20C03_AA02_44B8_8E15_FF084269166A__INCLUDED_)
