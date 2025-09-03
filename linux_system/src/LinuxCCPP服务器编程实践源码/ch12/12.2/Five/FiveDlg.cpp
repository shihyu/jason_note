//zww
// FiveDlg.cpp : implementation file
//

#include "stdafx.h"
#include "Five.h"
#include "FiveDlg.h"
#include "ServerDlg.h"
#include "ClientDlg.h"
#include "AboutDlg.h"
#include "Table.h"
#include "cmd.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

extern CFiveApp theApp;
/////////////////////////////////////////////////////////////////////////////
// CFiveDlg dialog

CFiveDlg::CFiveDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CFiveDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CFiveDlg)
    //}}AFX_DATA_INIT
    // Note that LoadIcon does not require a subsequent DestroyIcon in Win32
    m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CFiveDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CFiveDlg)
    DDX_Control(pDX, IDC_EDT_CHAT, m_ChatList);
    //}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CFiveDlg, CDialog)
    //{{AFX_MSG_MAP(CFiveDlg)
    ON_WM_PAINT()
    ON_WM_QUERYDRAGICON()

    ON_BN_CLICKED(IDC_BTN_BACK, OnBtnBack)
    ON_COMMAND(ID_MENU_SERVER, OnMenuServer)
    ON_COMMAND(ID_MENU_CLIENT, OnMenuClient)
    ON_WM_SETCURSOR()
    ON_BN_CLICKED(IDC_BTN_HQ, OnBtnHq)
    ON_BN_CLICKED(IDC_BTN_LOST, OnBtnLost)
    ON_COMMAND(ID_MENU_EXIT, OnMenuExit)
    ON_COMMAND(ID_MENU_ABOUT, OnMenuAbout)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CFiveDlg message handlers

BOOL CFiveDlg::OnInitDialog()
{
    CDialog::OnInitDialog();

    // Set the icon for this dialog.  The framework does this automatically
    //  when the application's main window is not a dialog
    SetIcon(m_hIcon, TRUE);			// Set big icon
    SetIcon(m_hIcon, FALSE);		// Set small icon

    // TODO: Add extra initialization here
    m_pDlg = NULL;
    CRect rect(0, 0, 200, 200);
    m_Table.CreateEx( WS_EX_CLIENTEDGE, _T("ChessTable"), NULL,   WS_VISIBLE | WS_BORDER | WS_CHILD,
                      CRect( 0, 0, 401, 478 ), this, IDC_TABLE );
    // 设置双方姓名
    m_Table.m_strMe = theApp.m_strName;
    SetDlgItemText( IDC_ST_ME, m_Table.m_strMe );
    SetDlgItemText( IDC_ST_ENEMY, _T("无玩家加入") );
    // 禁用“再玩”和“离开”
    CMenu *pMenu = GetMenu();
    pMenu->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_DISABLED | MF_GRAYED | MF_BYCOMMAND );
    pMenu->EnableMenuItem( ID_MENU_LEAVE, MF_DISABLED | MF_GRAYED | MF_BYCOMMAND );
    // 捕获聊天输入框句柄，供处理回车使用
    m_hChat = ::FindWindowEx( GetDlgItem( IDC_CMB_CHAT )->GetSafeHwnd(), NULL, _T("Edit"), NULL );
    ::SendMessage( m_hChat, EM_LIMITTEXT, (WPARAM)128, 0);
    m_Table.Clear( TRUE );
    GetDlgItem( IDC_CMB_CHAT )->EnableWindow( FALSE );
    GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );

    GetDlgItem( IDC_TABLE )->SetFocus();



    if(theApp.m_isCreator==0)  	PostMessage(WM_COMMAND, ID_MENU_CLIENT, 0);
    else if (theApp.m_isCreator == 1) 	PostMessage(WM_COMMAND, ID_MENU_SERVER, 0);


    return FALSE;  // return TRUE  unless you set the focus to a control
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CFiveDlg::OnPaint()
{
    if (IsIconic())
    {
        CPaintDC dc(this); // device context for painting

        SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

        // Center icon in client rectangle
        int cxIcon = GetSystemMetrics(SM_CXICON);
        int cyIcon = GetSystemMetrics(SM_CYICON);
        CRect rect;
        GetClientRect(&rect);
        int x = (rect.Width() - cxIcon + 1) / 2;
        int y = (rect.Height() - cyIcon + 1) / 2;

        // Draw the icon
        dc.DrawIcon(x, y, m_hIcon);
    }
    else
    {
        CDialog::OnPaint();
    }
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CFiveDlg::OnQueryDragIcon()
{
    return (HCURSOR) m_hIcon;
}

void CFiveDlg::OnOK()
{
}

void CFiveDlg::OnCancel()
{
    if (IDYES == MessageBox(_T("确定要退出吗？"), _T("五子棋"), MB_ICONQUESTION | MB_YESNO | MB_DEFBUTTON2))
    {
        CString strName, strInfo;
        int len;
        strInfo.Format(_T("%c,%s"), CL_CMD_OFFLINE, theApp.m_strName);//下线通知
        len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
        if (SOCKET_ERROR == len)
            AfxMessageBox(_T("发送错误"));
        CDialog::OnCancel();
    }
}



void CFiveDlg::OnBtnBack()
{
    // TODO: Add your control notification handler code here
    m_Table.Back();
}


void CFiveDlg::OnMenuServer()
{
    // TODO: Add your command handler code here
    m_pDlg = new CServerDlg;
    m_pDlg->Create( IDD_DLG_SERVER, this );
    m_pDlg->ShowWindow( SW_SHOW );
}

void CFiveDlg::OnMenuClient()
{
    // TODO: Add your command handler code here
    CClientDlg dlg;
    if ( IDOK == dlg.DoModal() )
    {
        // 发送己方姓名
        MSGSTRUCT msg;
        msg.uMsg = MSG_INFORMATION;
        lstrcpy( msg.szMsg, m_Table.m_strMe );

        m_Table.m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
        // 设置按钮状态
        GetDlgItem( IDC_BTN_HQ )->EnableWindow( TRUE );
        GetDlgItem( IDC_CMB_CHAT )->EnableWindow( TRUE );
        GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        GetDlgItem( IDC_BTN_LOST )->EnableWindow( TRUE );
        // 设置菜单状态
        m_Table.SetMenuState( FALSE );
    }
}

BOOL CFiveDlg::OnSetCursor(CWnd* pWnd, UINT nHitTest, UINT message)
{
    // TODO: Add your message handler code here and/or call default
    if ( GetDlgItem( IDC_EDT_CHAT ) == pWnd )
    {
        // 处理聊天记录的鼠标指针
        SetCursor( LoadCursor( NULL, IDC_ARROW ) );
        return TRUE;
    }
    else
        return CDialog::OnSetCursor(pWnd, nHitTest, message);
}

BOOL CFiveDlg::PreTranslateMessage(MSG* pMsg)
{
    // TODO: Add your specialized code here and/or call the base class
    if ( WM_KEYDOWN == pMsg->message && VK_RETURN == pMsg->wParam && m_hChat == pMsg->hwnd )
    {
        // 处理聊天输入窗口的回车消息
        TCHAR str[128];
        // 发送聊天内容
        ::GetWindowText( m_hChat, str, 128 );
        m_Table.Chat( str );
        // 加入聊天记录
        CString strAdd;
        strAdd.Format( _T("你 说：%s\r\n"), str );
        m_ChatList.SetSel( -1, -1, TRUE );
        m_ChatList.ReplaceSel( strAdd );
        // 清空聊天输入窗口
        ::SetWindowText( m_hChat, _T("") );
    }
    return CDialog::PreTranslateMessage(pMsg);
}

void CFiveDlg::OnBtnHq()
{
    // TODO: Add your control notification handler code here
    m_Table.DrawGame();
}

void CFiveDlg::OnBtnLost()
{
    // TODO: Add your control notification handler code here
    m_Table.GiveUp();
}






void CFiveDlg::OnMenuExit()
{
    // TODO: Add your command handler code here
    OnCancel();
}

void CFiveDlg::OnMenuAbout()
{
    // TODO: Add your command handler code here
    CAboutDlg dlg;
    dlg.DoModal();
}


BOOL CFiveDlg::PreCreateWindow(CREATESTRUCT& cs)
{
    // TODO: 在此添加专用代码和/或调用基类

    return CDialog::PreCreateWindow(cs);
}
