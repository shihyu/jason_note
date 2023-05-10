//zww
// FiveDlg.h : header file
//

#if !defined(AFX_FIVEDLG_H__BF03957A_2042_4BEA_9B2C_EA217FF69B64__INCLUDED_)
#define AFX_FIVEDLG_H__BF03957A_2042_4BEA_9B2C_EA217FF69B64__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "Table.h"
#include "FiveSocket.h"	// Added by ClassView
/////////////////////////////////////////////////////////////////////////////
// CFiveDlg dialog

class CFiveDlg : public CDialog
{
// Construction
public:
    CDialog * m_pDlg;
    CFiveDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
    //{{AFX_DATA(CFiveDlg)
    enum { IDD = IDD_FIVE_DIALOG };
    CEdit	m_ChatList;
    CTable m_Table;
    //}}AFX_DATA

    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CFiveDlg)
public:
    virtual BOOL PreTranslateMessage(MSG* pMsg);
protected:
    virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
    //}}AFX_VIRTUAL

// Implementation
protected:
    HWND m_hChat;
    HICON m_hIcon;

    // Generated message map functions
    //{{AFX_MSG(CFiveDlg)
    virtual BOOL OnInitDialog();
    afx_msg void OnPaint();
    afx_msg HCURSOR OnQueryDragIcon();
    virtual void OnOK();
    virtual void OnCancel();
    afx_msg void OnBtnBack();
    afx_msg void OnMenuServer();
    afx_msg void OnMenuClient();
    afx_msg BOOL OnSetCursor(CWnd* pWnd, UINT nHitTest, UINT message);
    afx_msg void OnBtnHq();
    afx_msg void OnBtnLost();
    afx_msg void OnMenuExit();
    afx_msg void OnMenuAbout();
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
    virtual BOOL PreCreateWindow(CREATESTRUCT& cs);
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_FIVEDLG_H__BF03957A_2042_4BEA_9B2C_EA217FF69B64__INCLUDED_)
