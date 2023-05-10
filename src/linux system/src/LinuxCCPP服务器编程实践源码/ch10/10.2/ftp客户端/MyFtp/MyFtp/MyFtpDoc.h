//created by zww
// MyFtpDoc.h : interface of the CMyFtpDoc class
//
/////////////////////////////////////////////////////////////////////////////

#if !defined(AFX_MYFTPDOC_H__09135002_98D8_4DB0_8C3F_59A486FBD68E__INCLUDED_)
#define AFX_MYFTPDOC_H__09135002_98D8_4DB0_8C3F_59A486FBD68E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000


class CMyFtpDoc : public CDocument
{
protected: // create from serialization only
    CMyFtpDoc();
    DECLARE_DYNCREATE(CMyFtpDoc)

// Attributes
public:

// Operations
public:

// Overrides
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CMyFtpDoc)
public:
    virtual BOOL OnNewDocument();
    virtual void Serialize(CArchive& ar);
    //}}AFX_VIRTUAL

// Implementation
public:
    virtual ~CMyFtpDoc();
#ifdef _DEBUG
    virtual void AssertValid() const;
    virtual void Dump(CDumpContext& dc) const;
#endif

protected:

// Generated message map functions
protected:
    //{{AFX_MSG(CMyFtpDoc)
    // NOTE - the ClassWizard will add and remove member functions here.
    //    DO NOT EDIT what you see in these blocks of generated code !
    //}}AFX_MSG
    DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MYFTPDOC_H__09135002_98D8_4DB0_8C3F_59A486FBD68E__INCLUDED_)
