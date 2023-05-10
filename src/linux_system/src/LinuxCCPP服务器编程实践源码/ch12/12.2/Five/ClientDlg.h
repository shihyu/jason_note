//zww
#if !defined(AFX_CLIENTDLG_H__09592A7A_9AD7_4D2E_88D2_068656848D79__INCLUDED_)
#define AFX_CLIENTDLG_H__09592A7A_9AD7_4D2E_88D2_068656848D79__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ClientDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CClientDlg dialog

class CClientDlg : public CDialog
{
// Construction
public:
    void CClientDlg::Connect();
    CClientDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
    //{{AFX_DATA(CClientDlg)
    enum { IDD = IDD_DLG_CLIENT };
    // NOTE: the ClassWizard will add data members here
    //}}AFX_DATA


// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CClientDlg)
protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
    //}}AFX_VIRTUAL

// Implementation
protected:

    // Generated message map functions
    //{{AFX_MSG(CClientDlg)
    virtual void OnOK();
    afx_msg void OnBtnOut();
    afx_msg void OnUpdateEditHost();
    virtual BOOL OnInitDialog();
    afx_msg void OnTimer(UINT nIDEvent);
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
private:
    int m_nTimer;
    CTable *m_pTable;
public:
    CEdit m_edtHost;
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CLIENTDLG_H__09592A7A_9AD7_4D2E_88D2_068656848D79__INCLUDED_)
