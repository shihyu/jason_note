//created by zww
// ConnectDlg.cpp : implementation file
//

#include "stdafx.h"
#include "MyFtp.h"
#include "ConnectDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CConnectDlg dialog


CConnectDlg::CConnectDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CConnectDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CConnectDlg)
    m_FtpWebSite = _T("192.168.11.129");
    m_UserName = _T("anonymous");
    m_UserPwd = _T("");
    //}}AFX_DATA_INIT
}


void CConnectDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CConnectDlg)
    DDX_Text(pDX, IDC_EDIT1, m_FtpWebSite);
    DDX_Text(pDX, IDC_EDIT2, m_UserName);
    DDX_Text(pDX, IDC_EDIT3, m_UserPwd);
    //}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CConnectDlg, CDialog)
    //{{AFX_MSG_MAP(CConnectDlg)
    ON_BN_CLICKED(IDOK, OnConnect)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CConnectDlg message handlers

void CConnectDlg::OnConnect()
{
    // TODO: Add your control notification handler code here
    UpdateData();

    CDialog::OnOK();
}
