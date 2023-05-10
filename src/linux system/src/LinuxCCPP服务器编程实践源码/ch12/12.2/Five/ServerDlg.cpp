//zww
// ServerDlg.cpp : implementation file
//

#include "stdafx.h"
#include "five.h"
#include "ServerDlg.h"
#include "Table.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CServerDlg dialog


CServerDlg::CServerDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CServerDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CServerDlg)
    // NOTE: the ClassWizard will add member initialization here
    //}}AFX_DATA_INIT
}


void CServerDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CServerDlg)
    // NOTE: the ClassWizard will add DDX and DDV calls here
    //}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CServerDlg, CDialog)
    //{{AFX_MSG_MAP(CServerDlg)
    ON_BN_CLICKED(IDC_BTN_LEAVE, OnBtnLeave)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CServerDlg message handlers

BOOL CServerDlg::OnInitDialog()
{
    CDialog::OnInitDialog();

    // TODO: Add extra initialization here

    // 首先禁用主窗口达到模式对话框的目的
    GetParent()->EnableWindow( FALSE );
    // 获取主机名及IP地址
    CHAR szHost[100];
    CHAR *szIP;
    hostent *host;

    gethostname(szHost, 100);
    SetDlgItemText( IDC_EDIT_HOST, szHost );

    host = gethostbyname( szHost );
    for ( int i = 0; host != NULL && host->h_addr_list[i] != NULL; i++ )
    {
        szIP = inet_ntoa( *( (in_addr *)host->h_addr_list[i] ) );
        break;
    }
    SetDlgItemText( IDC_EDIT_IP, szIP );

    startGame();
    return FALSE;  // return TRUE unless you set the focus to a control
    // EXCEPTION: OCX Property Pages should return FALSE
}

void CServerDlg::OnBtnLeave()
{
    // TODO: Add your control notification handler code here
    OnCancel();
}

void CServerDlg::startGame()
{
    // TODO: Add your control notification handler code here
    CTable *pTable = (CTable *)GetParent()->GetDlgItem( IDC_TABLE );
    SetDlgItemText( IDC_ST_STATUS, _T("状态：等待其他玩家加入...") );
    pTable->m_sock.Create( 20000 );
    pTable->m_sock.Listen();

}

void CServerDlg::OnCancel()
{
    // TODO: Add extra cleanup here
    CTable *pTable = (CTable *)GetParent()->GetDlgItem( IDC_TABLE );
    pTable->m_sock.Close();

    CDialog::OnCancel();
}
