//zww
// FiveSocket.cpp : implementation file
//

#include "stdafx.h"
#include "five.h"
#include "FiveSocket.h"
#include "Table.h"
#include "FiveDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CFiveSocket

CFiveSocket::CFiveSocket()
{
}

CFiveSocket::~CFiveSocket()
{
}


// Do not edit the following lines, which are needed by ClassWizard.
#if 0
BEGIN_MESSAGE_MAP(CFiveSocket, CAsyncSocket)
    //{{AFX_MSG_MAP(CFiveSocket)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()
#endif	// 0

/////////////////////////////////////////////////////////////////////////////
// CFiveSocket member functions

void CFiveSocket::OnAccept( int nErrorCode )
{
    CFiveDlg *pDlg = (CFiveDlg *)AfxGetMainWnd();
    // 使本窗口生效
    pDlg->EnableWindow();
    delete []pDlg->m_pDlg;
    pDlg->m_pDlg = NULL;
    pDlg->m_Table.Accept( 2 );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( TRUE );
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_CMB_CHAT )->EnableWindow( TRUE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( TRUE );
    pDlg->m_Table.SetMenuState( FALSE );
}

void CFiveSocket::OnClose( int nErrorCode )
{
    CFiveDlg *pDlg = (CFiveDlg *)AfxGetMainWnd();
    pDlg->MessageBox( _T("对方已经离开游戏，改日再较量不迟。"), _T("五子棋"), MB_ICONINFORMATION);
    // 禁用所有项目，并使菜单生效
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_CMB_CHAT )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
    pDlg->m_Table.SetMenuState( TRUE );
    pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_BYCOMMAND | MF_GRAYED | MF_DISABLED );
    pDlg->m_Table.SetWait( TRUE );
    // 重新设置对方姓名
    pDlg->SetDlgItemText( IDC_ST_ENEMY, _T("无玩家加入") );
}

void CFiveSocket::OnConnect( int nErrorCode )
{
    CTable *pTable = (CTable *)AfxGetMainWnd()->GetDlgItem( IDC_TABLE );
    pTable->m_bConnected = TRUE;
    pTable->Connect( 2 );
}

void CFiveSocket::OnReceive( int nErrorCode )
{
    CTable *pTable = (CTable *)AfxGetMainWnd()->GetDlgItem( IDC_TABLE );
    pTable->Receive();
}
