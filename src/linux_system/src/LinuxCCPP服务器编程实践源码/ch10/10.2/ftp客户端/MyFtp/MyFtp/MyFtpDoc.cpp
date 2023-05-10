//created by zww
// MyFtpDoc.cpp : implementation of the CMyFtpDoc class
//

#include "stdafx.h"
#include "MyFtp.h"

#include "MyFtpDoc.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMyFtpDoc

IMPLEMENT_DYNCREATE(CMyFtpDoc, CDocument)

BEGIN_MESSAGE_MAP(CMyFtpDoc, CDocument)
    //{{AFX_MSG_MAP(CMyFtpDoc)
    // NOTE - the ClassWizard will add and remove mapping macros here.
    //    DO NOT EDIT what you see in these blocks of generated code!
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMyFtpDoc construction/destruction

CMyFtpDoc::CMyFtpDoc()
{
    // TODO: add one-time construction code here

}

CMyFtpDoc::~CMyFtpDoc()
{
}

BOOL CMyFtpDoc::OnNewDocument()
{
    if (!CDocument::OnNewDocument())
        return FALSE;

    // TODO: add reinitialization code here
    // (SDI documents will reuse this document)

    return TRUE;
}



/////////////////////////////////////////////////////////////////////////////
// CMyFtpDoc serialization

void CMyFtpDoc::Serialize(CArchive& ar)
{
    if (ar.IsStoring())
    {
        // TODO: add storing code here
    }
    else
    {
        // TODO: add loading code here
    }
}

/////////////////////////////////////////////////////////////////////////////
// CMyFtpDoc diagnostics

#ifdef _DEBUG
void CMyFtpDoc::AssertValid() const
{
    CDocument::AssertValid();
}

void CMyFtpDoc::Dump(CDumpContext& dc) const
{
    CDocument::Dump(dc);
}
#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CMyFtpDoc commands
