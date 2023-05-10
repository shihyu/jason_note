//Download by http://www.NewXing.com
#if !defined(AFX_CHATEDIT_H__8A9F712D_68AC_4B70_B28F_920FA67B597F__INCLUDED_)
#define AFX_CHATEDIT_H__8A9F712D_68AC_4B70_B28F_920FA67B597F__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ChatEdit.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CChatEdit window

class CChatEdit : public CEdit
{
// Construction
public:
    CChatEdit();

// Attributes
public:

// Operations
public:

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CChatEdit)
    //}}AFX_VIRTUAL

// Implementation
public:
    virtual ~CChatEdit();

    // Generated message map functions
protected:
    //{{AFX_MSG(CChatEdit)
    afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);
    //}}AFX_MSG

    DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHATEDIT_H__8A9F712D_68AC_4B70_B28F_920FA67B597F__INCLUDED_)
