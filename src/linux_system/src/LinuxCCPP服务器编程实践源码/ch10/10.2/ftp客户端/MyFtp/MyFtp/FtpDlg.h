//zww add
#if !defined(AFX_FTPDLG_H__C22AAC8E_C843_4D8D_8A3D_1E7ABF7697A3__INCLUDED_)
#define AFX_FTPDLG_H__C22AAC8E_C843_4D8D_8A3D_1E7ABF7697A3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// FtpDlg.h : header file
//
#include "NewNameDlg.h"
/////////////////////////////////////////////////////////////////////////////
// CFtpDlg dialog

class CFtpDlg : public CDialog
{
// Construction
public:
    CFtpDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
    //{{AFX_DATA(CFtpDlg)
    enum { IDD = IDD_DIALOG2 };
    CButton	m_BtnDelete;
    CButton	m_BtnRename;
    CButton	m_BtnQuery;
    CButton	m_BtnUpLoad;
    CButton	m_BtnDownLoad;
    CListCtrl	m_FtpFile;
    //}}AFX_DATA
    CFtpConnection* m_pConnection;
    CFtpFileFind* m_pFileFind;

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CFtpDlg)
protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
    //}}AFX_VIRTUAL
    //Ìí¼ÓµÄº¯Êý
    void ListContent(LPCTSTR );
    void GetLastDiretory(CString &str);
// Implementation
protected:

    // Generated message map functions
    //{{AFX_MSG(CFtpDlg)
    afx_msg void OnQuary();
    virtual BOOL OnInitDialog();
    afx_msg void OnExit();
    afx_msg void OnDownload();
    afx_msg void OnUpload();
    afx_msg void OnRename();
    afx_msg void OnDelete();
    afx_msg void OnNextdirectory();
    afx_msg void OnLastdirectory();
    afx_msg void OnDblclkListFile(NMHDR* pNMHDR, LRESULT* pResult);
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_FTPDLG_H__C22AAC8E_C843_4D8D_8A3D_1E7ABF7697A3__INCLUDED_)
