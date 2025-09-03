//created by zww
#if !defined(AFX_NEWNAMEDLG_H__0F28D37E_EA50_4367_93A5_802021016047__INCLUDED_)
#define AFX_NEWNAMEDLG_H__0F28D37E_EA50_4367_93A5_802021016047__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// NewNameDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CNewNameDlg dialog

class CNewNameDlg : public CDialog
{
// Construction
public:
    CNewNameDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
    //{{AFX_DATA(CNewNameDlg)
    enum { IDD = IDD_DIALOG3 };
    CString	m_NewFileName;
    //}}AFX_DATA


// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CNewNameDlg)
protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
    //}}AFX_VIRTUAL

// Implementation
protected:

    // Generated message map functions
    //{{AFX_MSG(CNewNameDlg)
    virtual void OnOK();
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_NEWNAMEDLG_H__0F28D37E_EA50_4367_93A5_802021016047__INCLUDED_)
