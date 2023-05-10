//zww
#include "stdafx.h"
#include "Five.h"
#include "Table.h"
#include "Messages.h"
#include "Resource.h"
#include "cmd.h"

extern CFiveApp theApp;

//////////////////////////////////////////////////////////////////////////
// 构造函数，初始化棋盘数据以及图像数据
//////////////////////////////////////////////////////////////////////////
CTable::CTable()
{
    // 初始化玩家姓名
    TCHAR str[10];
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    ::GetPrivateProfileString( _T("Options"), _T("Name"), _T("Renjiu"), str, 15, pApp->m_szIni );
    m_strMe = str;
    // 初始化图像列表
    m_iml.Create( 24, 24, ILC_COLOR24 | ILC_MASK, 0, 2 );
    // 载入黑、白棋子掩码位图
    CBitmap bmpBlack, bmpWhite;
    bmpBlack.LoadBitmap( IDB_BMP_BLACK );
    m_iml.Add( &bmpBlack, 0xff00ff );
    bmpWhite.LoadBitmap( IDB_BMP_WHITE );
    m_iml.Add( &bmpWhite, 0xff00ff );
    // 初始化游戏模式
    m_pGame = NULL;
}
//////////////////////////////////////////////////////////////////////////
// 析构函数，释放m_pGame指针
//////////////////////////////////////////////////////////////////////////
CTable::~CTable()
{
    // 写入玩家姓名
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    ::WritePrivateProfileString( _T("Options"), _T("Name"), m_strMe, pApp->m_szIni );
    // 写入战绩统计
    TCHAR str[10];
    wsprintf( str, _T("%d"), pApp->m_nWin );
    ::WritePrivateProfileString( _T("Stats"), _T("Win"), str, pApp->m_szIni );
    wsprintf( str, _T("%d"), pApp->m_nDraw );
    ::WritePrivateProfileString( _T("Stats"), _T("Draw"), str, pApp->m_szIni );
    wsprintf( str, _T("%d"), pApp->m_nLost );
    ::WritePrivateProfileString( _T("Stats"), _T("Lost"), str, pApp->m_szIni );
    if ( NULL != m_pGame )
        delete m_pGame;
}
//////////////////////////////////////////////////////////////////////////
// 在指定棋盘坐标处绘制指定颜色的棋子
//////////////////////////////////////////////////////////////////////////
void CTable::Draw( int x, int y, int color )
{
    POINT pt;
    pt.x = 12 + 25 * x;
    pt.y = 84 + 25 * y;
    CDC *pDC = GetDC();
    CPen pen;
    pen.CreatePen( PS_SOLID, 1, 0xff );
    pDC->SelectObject( &pen );
    pDC->SetROP2( R2_NOTXORPEN );
    m_iml.Draw( pDC, color, pt, ILD_TRANSPARENT );
    STEP step;
    // 利用R2_NOTXORPEN擦除先前画出的矩形
    if ( !m_pGame->m_StepList.empty() )
    {
        // 获取最后一个点
        step = *( m_pGame->m_StepList.begin() );
        pDC->MoveTo( 11 + 25 * step.x, 83 + 25 * step.y );
        pDC->LineTo( 36 + 25 * step.x, 83 + 25 * step.y );
        pDC->LineTo( 36 + 25 * step.x, 108 + 25 * step.y );
        pDC->LineTo( 11 + 25 * step.x, 108 + 25 * step.y );
        pDC->LineTo( 11 + 25 * step.x, 83 + 25 * step.y );
    }
    // 更新最后落子坐标数据，画新的矩形
    step.color = color;
    step.x = x;
    step.y = y;
    m_pGame->m_StepList.push_front( step );
    pDC->MoveTo( 11 + 25 * step.x, 83 + 25 * step.y );
    pDC->LineTo( 36 + 25 * step.x, 83 + 25 * step.y );
    pDC->LineTo( 36 + 25 * step.x, 108 + 25 * step.y );
    pDC->LineTo( 11 + 25 * step.x, 108 + 25 * step.y );
    pDC->LineTo( 11 + 25 * step.x, 83 + 25 * step.y );
    ReleaseDC( pDC );
}
//////////////////////////////////////////////////////////////////////////
// 清空棋盘
//////////////////////////////////////////////////////////////////////////
void CTable::Clear( BOOL bWait )
{
    int x, y;
    for ( y = 0; y < 15; y++ )
    {
        for ( x = 0; x < 15; x++ )
        {
            m_data[x][y] = -1;
        }
    }
    // 设置等待标志
    m_bWait = bWait;
    Invalidate();
    // 删除游戏
    if ( m_pGame != NULL )
    {
        delete m_pGame;
        m_pGame = NULL;
    }
}
//////////////////////////////////////////////////////////////////////////
// 设置玩家颜色
//////////////////////////////////////////////////////////////////////////
void CTable::SetColor( int color )
{
    m_color = color;
}
//////////////////////////////////////////////////////////////////////////
// 获取玩家颜色
//////////////////////////////////////////////////////////////////////////
int CTable::GetColor() const
{
    return m_color;
}
//////////////////////////////////////////////////////////////////////////
// 设置等待标志，返回先前的等待标志
//////////////////////////////////////////////////////////////////////////
BOOL CTable::SetWait( BOOL bWait )
{
    m_bOldWait = m_bWait;
    m_bWait = bWait;
    return m_bOldWait;
}
//////////////////////////////////////////////////////////////////////////
// 设置棋盘数据，并绘制棋子
//////////////////////////////////////////////////////////////////////////
void CTable::SetData( int x, int y, int color )
{
    m_data[x][y] = color;
    Draw( x, y, color );
}
//////////////////////////////////////////////////////////////////////////
// 判断指定颜色是否胜利
//////////////////////////////////////////////////////////////////////////
BOOL CTable::Win( int color ) const
{
    int x, y;
    // 判断横向
    for ( y = 0; y < 15; y++ )
    {
        for ( x = 0; x < 11; x++ )
        {
            if ( color == m_data[x][y] && color == m_data[x + 1][y] &&
                    color == m_data[x + 2][y] && color == m_data[x + 3][y] &&
                    color == m_data[x + 4][y] )
            {
                return TRUE;
            }
        }
    }
    // 判断纵向
    for ( y = 0; y < 11; y++ )
    {
        for ( x = 0; x < 15; x++ )
        {
            if ( color == m_data[x][y] && color == m_data[x][y + 1] &&
                    color == m_data[x][y + 2] && color == m_data[x][y + 3] &&
                    color == m_data[x][y + 4] )
            {
                return TRUE;
            }
        }
    }
    // 判断“\”方向
    for ( y = 0; y < 11; y++ )
    {
        for ( x = 0; x < 11; x++ )
        {
            if ( color == m_data[x][y] && color == m_data[x + 1][y + 1] &&
                    color == m_data[x + 2][y + 2] && color == m_data[x + 3][y + 3] &&
                    color == m_data[x + 4][y + 4] )
            {
                return TRUE;
            }
        }
    }
    // 判断“/”方向
    for ( y = 0; y < 11; y++ )
    {
        for ( x = 4; x < 15; x++ )
        {
            if ( color == m_data[x][y] && color == m_data[x - 1][y + 1] &&
                    color == m_data[x - 2][y + 2] && color == m_data[x - 3][y + 3] &&
                    color == m_data[x - 4][y + 4] )
            {
                return TRUE;
            }
        }
    }
    // 不满足胜利条件
    return FALSE;
}
//////////////////////////////////////////////////////////////////////////
// 发送再玩一次请求
//////////////////////////////////////////////////////////////////////////
void CTable::PlayAgain()
{
    MSGSTRUCT msg;
    msg.uMsg = MSG_PLAYAGAIN;
    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// 发送和棋请求
//////////////////////////////////////////////////////////////////////////
void CTable::DrawGame()
{
    CDialog *pDlg = (CDialog *)AfxGetMainWnd();
    // 使按钮失效
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );

    // 设置等待标志
    SetWait( TRUE );

    MSGSTRUCT msg;
    msg.uMsg = MSG_DRAW;
    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// 设置游戏模式
//////////////////////////////////////////////////////////////////////////
void CTable::SetGameMode( int nGameMode )
{
    if ( 1 == nGameMode )
        m_pGame = new COneGame( this );
    else
        m_pGame = new CTwoGame( this );
    m_pGame->Init();
}
//////////////////////////////////////////////////////////////////////////
// 悔棋
//////////////////////////////////////////////////////////////////////////
void CTable::Back()
{
    m_pGame->Back();
}
//////////////////////////////////////////////////////////////////////////
// 处理对方落子后的工作
//////////////////////////////////////////////////////////////////////////
void CTable::Over()
{
    // 判断对方是否胜利
    if ( Win( 1 - m_color ) )
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nLost++;
        CDialog *pDlg = (CDialog *)GetParent();
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_LOST ), NULL, SND_RESOURCE | SND_SYNC );
        pDlg->MessageBox( _T("您输了，不过不要灰心，失败乃成功之母哦！"), _T("失败"), MB_ICONINFORMATION );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        // 如果是网络对战，则生效“重玩”
        if ( m_bConnected )
        {
            pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
        }
        return;
    }
    m_bWait = FALSE;
}
//////////////////////////////////////////////////////////////////////////
// 设置菜单状态（主要为网络对战准备）
//////////////////////////////////////////////////////////////////////////
void CTable::SetMenuState( BOOL bEnable )
{
    UINT uEnable, uDisable;
    if ( bEnable )
    {
        uEnable = MF_ENABLED;
        uDisable = MF_GRAYED | MF_DISABLED;
    }
    else
    {
        uEnable = MF_GRAYED | MF_DISABLED;
        uDisable = MF_ENABLED;
    }
    CMenu *pMenu = GetParent()->GetMenu();
    pMenu->GetSubMenu( 0 )->EnableMenuItem( 0, uEnable | MF_BYPOSITION );
    pMenu->EnableMenuItem( ID_MENU_SERVER, uEnable );
    pMenu->EnableMenuItem( ID_MENU_CLIENT, uEnable );
    pMenu->EnableMenuItem( ID_MENU_LEAVE, uDisable );
    pMenu->EnableMenuItem( ID_MENU_PLAYAGAIN, uEnable );
}
//////////////////////////////////////////////////////////////////////////
// 接受连接
//////////////////////////////////////////////////////////////////////////
void CTable::Accept( int nGameMode )
{
    if ( 2 == nGameMode )
    {
        m_sock.Accept( m_conn );
    }
    m_bConnected = TRUE;

#if 1
    //客人来了，就要通知下服务器我不接客了。
    CString  strInfo;
    int len;


    strInfo.Format(_T("%c,%s"), CL_CMD_CREATOR_IS_BUSY, theApp.m_strName);//标记m_strName为忙状态
    len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));
#endif


    SetColor( 0 );
    Clear( FALSE );
    SetGameMode( nGameMode );
}
//////////////////////////////////////////////////////////////////////////
// 主动连接
//////////////////////////////////////////////////////////////////////////
void CTable::Connect( int nGameMode )
{
    SetColor( 1 );
    Clear( TRUE );
    SetGameMode( nGameMode );
}
//////////////////////////////////////////////////////////////////////////
// 发送聊天消息
//////////////////////////////////////////////////////////////////////////
void CTable::Chat( LPCTSTR lpszMsg )
{
    MSGSTRUCT msg;
    msg.uMsg = MSG_CHAT;
    lstrcpy( msg.szMsg, lpszMsg );

    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// 发送认输消息
//////////////////////////////////////////////////////////////////////////
void CTable::GiveUp()
{
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    pApp->m_nLost++;
    CDialog *pDlg = (CDialog *)AfxGetMainWnd();
    // 使按钮失效
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
    // 修改等待状态
    SetWait( TRUE );
    // 生效菜单项
    CMenu *pMenu = pDlg->GetMenu();
    pMenu->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );

    // 发送认输消息
    MSGSTRUCT msg;
    msg.uMsg = MSG_GIVEUP;

    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// 接收来自对方的数据
//////////////////////////////////////////////////////////////////////////
void CTable::Receive()
{
    MSGSTRUCT msgRecv;
    m_pGame->ReceiveMsg( &msgRecv );
    // 对各种消息分别进行处理
    switch ( msgRecv.uMsg )
    {
    case MSG_PUTSTEP:
    {
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_PUT ), NULL, SND_RESOURCE | SND_SYNC );
        SetData( msgRecv.x, msgRecv.y, msgRecv.color );
        // 大于1步才能悔棋
        GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
        Over();
    }
    break;
    case MSG_BACK:
    {
        if ( IDYES == GetParent()->MessageBox( _T("对方请求悔棋，接受这个请求吗？"),
                                               _T("悔棋"), MB_ICONQUESTION | MB_YESNO ) )
        {
            // 发送允许悔棋消息
            MSGSTRUCT msg;
            msg.uMsg = MSG_AGREEBACK;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
            // 给自己悔棋
            STEP step;
            step = *( m_pGame->m_StepList.begin() );
            m_pGame->m_StepList.pop_front();
            m_data[step.x][step.y] = -1;
            step = *( m_pGame->m_StepList.begin() );
            m_pGame->m_StepList.pop_front();
            m_data[step.x][step.y] = -1;
            // 大于1步才能悔棋
            GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
            Invalidate();
        }
        else
        {
            // 发送不允许悔棋消息
            MSGSTRUCT msg;
            msg.uMsg = MSG_REFUSEBACK;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
        }
    }
    break;
    case MSG_REFUSEBACK:
    {
        CDialog *pDlg = (CDialog *)AfxGetMainWnd();
        pDlg->MessageBox( _T("很抱歉，对方拒绝了您的悔棋请求。"), _T("悔棋"), MB_ICONINFORMATION );
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();
        RestoreWait();
    }
    break;
    case MSG_AGREEBACK:
    {
        STEP step;
        step = *( m_pGame->m_StepList.begin() );
        m_pGame->m_StepList.pop_front();
        m_data[step.x][step.y] = -1;
        step = *( m_pGame->m_StepList.begin() );
        m_pGame->m_StepList.pop_front();
        m_data[step.x][step.y] = -1;

        CDialog *pDlg = (CDialog *)AfxGetMainWnd();
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();
        // 大于1步才能悔棋
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
        RestoreWait();
        Invalidate();
    }
    break;
    case MSG_DRAW:
    {
        if ( IDYES == GetParent()->MessageBox( _T("对方请求和棋，接受这个请求吗？"),
                                               _T("和棋"), MB_ICONQUESTION | MB_YESNO ) )
        {
            CFiveApp *pApp = (CFiveApp *)AfxGetApp();
            pApp->m_nDraw++;
            // 发送允许和棋消息
            MSGSTRUCT msg;
            msg.uMsg = MSG_AGREEDRAW;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
            // 和棋后，禁用按钮和棋盘
            CDialog *pDlg = (CDialog *)GetParent();
            pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
            SetWait( TRUE );
            // 使“重玩”菜单生效
            pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
        }
        else
        {
            // 发送拒绝和棋消息
            MSGSTRUCT msg;
            msg.uMsg = MSG_REFUSEDRAW;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
        }
    }
    break;
    case MSG_AGREEDRAW:
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nDraw++;
        CDialog *pDlg = (CDialog *)GetParent();
        pDlg->MessageBox( _T("看来真是棋逢对手，对方接受了您的和棋请求。"), _T("和棋"), MB_ICONINFORMATION );
        // 和棋后，使“重玩”菜单生效
        pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
    }
    break;
    case MSG_REFUSEDRAW:
    {
        CDialog *pDlg = (CDialog *)GetParent();
        pDlg->MessageBox( _T("看来对方很有信心取得胜利，所以拒绝了您的和棋请求。"),
                          _T("和棋"), MB_ICONINFORMATION );
        // 重新设置按钮状态，并恢复棋盘状态
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();
        RestoreWait();
    }
    break;
    case MSG_CHAT:
    {
        CString strAdd;
        strAdd.Format( _T("%s 说：%s\r\n"), m_strAgainst, msgRecv.szMsg );
        CEdit *pEdit = (CEdit *)GetParent()->GetDlgItem( IDC_EDT_CHAT );
        pEdit->SetSel( -1, -1, TRUE );
        pEdit->ReplaceSel( strAdd );
    }
    break;
    case MSG_INFORMATION:
    {
        m_strAgainst = msgRecv.szMsg;
        GetParent()->GetDlgItem( IDC_ST_ENEMY )->SetWindowText( m_strAgainst );

        // 在先手接到姓名信息后，回返自己的姓名信息
        if ( 0 == m_color )
        {
            MSGSTRUCT msg;
            msg.uMsg = MSG_INFORMATION;
            lstrcpy( msg.szMsg, m_strMe );

            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
        }
    }
    break;
    case MSG_GIVEUP:
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nWin++;
        CDialog *pDlg = (CDialog *)GetParent();
        pDlg->MessageBox( _T("对方已经投子认输，恭喜您不战而屈人之兵！"), _T("胜利"), MB_ICONINFORMATION );
        // 禁用各按钮及棋盘
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        SetWait( TRUE );
        // 设置“重玩”为真
        pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
    }
    break;
    case MSG_PLAYAGAIN:
    {
        CDialog *pDlg = (CDialog *)GetParent();
        if ( IDYES == pDlg->MessageBox( _T("对方看来意犹未尽，请求与您再战一局，接受这个请求吗？\n\n选“否”将断开与他的连接。"),
                                        _T("再战"), MB_YESNO | MB_ICONQUESTION ) )
        {
            pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
            pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();

            MSGSTRUCT msg;
            msg.uMsg = MSG_AGREEAGAIN;

            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );

            Clear( (BOOL)m_color );
            SetGameMode( 2 );
        }
        else
        {
            m_conn.Close();
            m_sock.Close();
            pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_CMB_CHAT )->EnableWindow( FALSE );
            // 设置菜单状态
            SetMenuState( TRUE );
            // 设置棋盘等待状态
            SetWait( TRUE );
            // 设置网络连接状态
            m_bConnected = FALSE;
            // 重新设置玩家名称
            pDlg->SetDlgItemText( IDC_ST_ENEMY, _T("无玩家加入") );
        }
    }
    break;
    case MSG_AGREEAGAIN:
    {
        CDialog *pDlg = (CDialog *)GetParent();
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();
        Clear( (BOOL)m_color );
        SetGameMode( 2 );
    }
    break;
    }
}
// 消息映射表
BEGIN_MESSAGE_MAP( CTable, CWnd )
    //{{AFX_MSG_MAP(CTable)
    ON_WM_PAINT()
    ON_WM_LBUTTONUP()
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

//////////////////////////////////////////////////////////////////////////
// 处理WM_PAINT消息
//////////////////////////////////////////////////////////////////////////
void CTable::OnPaint()
{
    CPaintDC dc( this );
    CDC MemDC;
    MemDC.CreateCompatibleDC( &dc );
    // 装载棋盘
    CBitmap bmp;
    CPen pen;
    bmp.LoadBitmap( IDB_BMP_QP );
    pen.CreatePen( PS_SOLID, 1, 0xff );
    MemDC.SelectObject( &bmp );
    MemDC.SelectObject( &pen );
    MemDC.SetROP2( R2_NOTXORPEN );
    // 根据棋盘数据绘制棋子
    int x, y;
    POINT pt;
    for ( y = 0; y < 15; y++ )
    {
        for ( x = 0; x < 15; x++ )
        {
            if ( -1 != m_data[x][y] )
            {
                pt.x = 12 + 25 * x;
                pt.y = 84 + 25 * y;
                m_iml.Draw( &MemDC, m_data[x][y], pt, ILD_TRANSPARENT );
            }
        }
    }
    // 绘制最后落子的指示矩形
    if ( NULL != m_pGame && !m_pGame->m_StepList.empty() )
    {
        STEP step = *( m_pGame->m_StepList.begin() );
        MemDC.MoveTo( 11 + 25 * step.x, 83 + 25 * step.y );
        MemDC.LineTo( 36 + 25 * step.x, 83 + 25 * step.y );
        MemDC.LineTo( 36 + 25 * step.x, 108 + 25 * step.y );
        MemDC.LineTo( 11 + 25 * step.x, 108 + 25 * step.y );
        MemDC.LineTo( 11 + 25 * step.x, 83 + 25 * step.y );
    }
    // 完成绘制
    dc.BitBlt( 0, 0, 395, 472, &MemDC,0, 0, SRCCOPY );
}
//////////////////////////////////////////////////////////////////////////
// 处理左键弹起消息，为玩家落子之用
//////////////////////////////////////////////////////////////////////////
void CTable::OnLButtonUp( UINT nFlags, CPoint point )
{
    STEP stepPut;
    if ( m_bWait )
    {
        MessageBeep( MB_OK );
        return;
    }
    int x, y;
    x = ( point.x - 12 ) / 25;
    y = ( point.y - 84 ) / 25;
    // 如果在(0, 0)～(14, 14)范围内，且该坐标没有落子，则落子于此，否则发声警告并退出过程
    if ( x < 0 || x > 14 || y < 0 || y > 14 || m_data[x][y] != -1 )
    {
        MessageBeep( MB_OK );
        return;
    }
    else
    {
        // 如果位置合法，则落子
        SetData( x, y, m_color );
        stepPut.color = m_color;
        stepPut.x = x;
        stepPut.y = y;
        // 大于1步才能悔棋
        GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
    }
    // 判断胜利的情况
    if ( Win( m_color ) )
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nWin++;
        m_pGame->Win( stepPut );
        CDialog *pDlg = (CDialog *)GetParent();
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_WIN ), NULL, SND_SYNC | SND_RESOURCE );
        pDlg->MessageBox( _T("恭喜，您获得了胜利！"), _T("胜利"), MB_ICONINFORMATION );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        m_bWait = TRUE;
        return;
    }
    else
    {
        // 开始等待
        m_bWait = TRUE;
        // 发送落子信息
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_PUT ), NULL, SND_SYNC | SND_RESOURCE );
        m_pGame->SendStep( stepPut );
    }
}
//////////////////////////////////////////////////////////////////////////
// 重新设置先前的等待标志
//////////////////////////////////////////////////////////////////////////
void CTable::RestoreWait()
{
    SetWait( m_bOldWait );
}
