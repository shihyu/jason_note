//created by zww
// NewNameDlg.cpp : implementation file
//

#include "stdafx.h"
#include "myftp.h"
#include "NewNameDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CNewNameDlg dialog


CNewNameDlg::CNewNameDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CNewNameDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CNewNameDlg)
    m_NewFileName = _T("");
    //}}AFX_DATA_INIT
}


void CNewNameDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CNewNameDlg)
    DDX_Text(pDX, IDC_EDIT1, m_NewFileName);
    //}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CNewNameDlg, CDialog)
    //{{AFX_MSG_MAP(CNewNameDlg)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CNewNameDlg message handlers

void CNewNameDlg::OnOK()
{
    // TODO: Add extra validation here
    UpdateData();
    CDialog::OnOK();
}
