//zww
#include "stdafx.h"
#include "Five.h"
#include "Table.h"
#include "Messages.h"
#include "Resource.h"
#include "cmd.h"

extern CFiveApp theApp;

//////////////////////////////////////////////////////////////////////////
// ���캯������ʼ�����������Լ�ͼ������
//////////////////////////////////////////////////////////////////////////
CTable::CTable()
{
    // ��ʼ���������
    TCHAR str[10];
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    ::GetPrivateProfileString( _T("Options"), _T("Name"), _T("Renjiu"), str, 15, pApp->m_szIni );
    m_strMe = str;
    // ��ʼ��ͼ���б�
    m_iml.Create( 24, 24, ILC_COLOR24 | ILC_MASK, 0, 2 );
    // ����ڡ�����������λͼ
    CBitmap bmpBlack, bmpWhite;
    bmpBlack.LoadBitmap( IDB_BMP_BLACK );
    m_iml.Add( &bmpBlack, 0xff00ff );
    bmpWhite.LoadBitmap( IDB_BMP_WHITE );
    m_iml.Add( &bmpWhite, 0xff00ff );
    // ��ʼ����Ϸģʽ
    m_pGame = NULL;
}
//////////////////////////////////////////////////////////////////////////
// �����������ͷ�m_pGameָ��
//////////////////////////////////////////////////////////////////////////
CTable::~CTable()
{
    // д���������
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    ::WritePrivateProfileString( _T("Options"), _T("Name"), m_strMe, pApp->m_szIni );
    // д��ս��ͳ��
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
// ��ָ���������괦����ָ����ɫ������
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
    // ����R2_NOTXORPEN������ǰ�����ľ���
    if ( !m_pGame->m_StepList.empty() )
    {
        // ��ȡ���һ����
        step = *( m_pGame->m_StepList.begin() );
        pDC->MoveTo( 11 + 25 * step.x, 83 + 25 * step.y );
        pDC->LineTo( 36 + 25 * step.x, 83 + 25 * step.y );
        pDC->LineTo( 36 + 25 * step.x, 108 + 25 * step.y );
        pDC->LineTo( 11 + 25 * step.x, 108 + 25 * step.y );
        pDC->LineTo( 11 + 25 * step.x, 83 + 25 * step.y );
    }
    // ������������������ݣ����µľ���
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
// �������
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
    // ���õȴ���־
    m_bWait = bWait;
    Invalidate();
    // ɾ����Ϸ
    if ( m_pGame != NULL )
    {
        delete m_pGame;
        m_pGame = NULL;
    }
}
//////////////////////////////////////////////////////////////////////////
// ���������ɫ
//////////////////////////////////////////////////////////////////////////
void CTable::SetColor( int color )
{
    m_color = color;
}
//////////////////////////////////////////////////////////////////////////
// ��ȡ�����ɫ
//////////////////////////////////////////////////////////////////////////
int CTable::GetColor() const
{
    return m_color;
}
//////////////////////////////////////////////////////////////////////////
// ���õȴ���־��������ǰ�ĵȴ���־
//////////////////////////////////////////////////////////////////////////
BOOL CTable::SetWait( BOOL bWait )
{
    m_bOldWait = m_bWait;
    m_bWait = bWait;
    return m_bOldWait;
}
//////////////////////////////////////////////////////////////////////////
// �����������ݣ�����������
//////////////////////////////////////////////////////////////////////////
void CTable::SetData( int x, int y, int color )
{
    m_data[x][y] = color;
    Draw( x, y, color );
}
//////////////////////////////////////////////////////////////////////////
// �ж�ָ����ɫ�Ƿ�ʤ��
//////////////////////////////////////////////////////////////////////////
BOOL CTable::Win( int color ) const
{
    int x, y;
    // �жϺ���
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
    // �ж�����
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
    // �жϡ�\������
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
    // �жϡ�/������
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
    // ������ʤ������
    return FALSE;
}
//////////////////////////////////////////////////////////////////////////
// ��������һ������
//////////////////////////////////////////////////////////////////////////
void CTable::PlayAgain()
{
    MSGSTRUCT msg;
    msg.uMsg = MSG_PLAYAGAIN;
    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// ���ͺ�������
//////////////////////////////////////////////////////////////////////////
void CTable::DrawGame()
{
    CDialog *pDlg = (CDialog *)AfxGetMainWnd();
    // ʹ��ťʧЧ
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );

    // ���õȴ���־
    SetWait( TRUE );

    MSGSTRUCT msg;
    msg.uMsg = MSG_DRAW;
    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// ������Ϸģʽ
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
// ����
//////////////////////////////////////////////////////////////////////////
void CTable::Back()
{
    m_pGame->Back();
}
//////////////////////////////////////////////////////////////////////////
// ����Է����Ӻ�Ĺ���
//////////////////////////////////////////////////////////////////////////
void CTable::Over()
{
    // �ж϶Է��Ƿ�ʤ��
    if ( Win( 1 - m_color ) )
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nLost++;
        CDialog *pDlg = (CDialog *)GetParent();
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_LOST ), NULL, SND_RESOURCE | SND_SYNC );
        pDlg->MessageBox( _T("�����ˣ�������Ҫ���ģ�ʧ���˳ɹ�֮ĸŶ��"), _T("ʧ��"), MB_ICONINFORMATION );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        // ����������ս������Ч�����桱
        if ( m_bConnected )
        {
            pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
        }
        return;
    }
    m_bWait = FALSE;
}
//////////////////////////////////////////////////////////////////////////
// ���ò˵�״̬����ҪΪ�����ս׼����
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
// ��������
//////////////////////////////////////////////////////////////////////////
void CTable::Accept( int nGameMode )
{
    if ( 2 == nGameMode )
    {
        m_sock.Accept( m_conn );
    }
    m_bConnected = TRUE;

#if 1
    //�������ˣ���Ҫ֪ͨ�·������Ҳ��ӿ��ˡ�
    CString  strInfo;
    int len;


    strInfo.Format(_T("%c,%s"), CL_CMD_CREATOR_IS_BUSY, theApp.m_strName);//���m_strNameΪæ״̬
    len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("���ʹ���"));
#endif


    SetColor( 0 );
    Clear( FALSE );
    SetGameMode( nGameMode );
}
//////////////////////////////////////////////////////////////////////////
// ��������
//////////////////////////////////////////////////////////////////////////
void CTable::Connect( int nGameMode )
{
    SetColor( 1 );
    Clear( TRUE );
    SetGameMode( nGameMode );
}
//////////////////////////////////////////////////////////////////////////
// ����������Ϣ
//////////////////////////////////////////////////////////////////////////
void CTable::Chat( LPCTSTR lpszMsg )
{
    MSGSTRUCT msg;
    msg.uMsg = MSG_CHAT;
    lstrcpy( msg.szMsg, lpszMsg );

    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// ����������Ϣ
//////////////////////////////////////////////////////////////////////////
void CTable::GiveUp()
{
    CFiveApp *pApp = (CFiveApp *)AfxGetApp();
    pApp->m_nLost++;
    CDialog *pDlg = (CDialog *)AfxGetMainWnd();
    // ʹ��ťʧЧ
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
    // �޸ĵȴ�״̬
    SetWait( TRUE );
    // ��Ч�˵���
    CMenu *pMenu = pDlg->GetMenu();
    pMenu->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );

    // ����������Ϣ
    MSGSTRUCT msg;
    msg.uMsg = MSG_GIVEUP;

    m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
//////////////////////////////////////////////////////////////////////////
// �������ԶԷ�������
//////////////////////////////////////////////////////////////////////////
void CTable::Receive()
{
    MSGSTRUCT msgRecv;
    m_pGame->ReceiveMsg( &msgRecv );
    // �Ը�����Ϣ�ֱ���д���
    switch ( msgRecv.uMsg )
    {
    case MSG_PUTSTEP:
    {
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_PUT ), NULL, SND_RESOURCE | SND_SYNC );
        SetData( msgRecv.x, msgRecv.y, msgRecv.color );
        // ����1�����ܻ���
        GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
        Over();
    }
    break;
    case MSG_BACK:
    {
        if ( IDYES == GetParent()->MessageBox( _T("�Է�������壬�������������"),
                                               _T("����"), MB_ICONQUESTION | MB_YESNO ) )
        {
            // �������������Ϣ
            MSGSTRUCT msg;
            msg.uMsg = MSG_AGREEBACK;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
            // ���Լ�����
            STEP step;
            step = *( m_pGame->m_StepList.begin() );
            m_pGame->m_StepList.pop_front();
            m_data[step.x][step.y] = -1;
            step = *( m_pGame->m_StepList.begin() );
            m_pGame->m_StepList.pop_front();
            m_data[step.x][step.y] = -1;
            // ����1�����ܻ���
            GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
            Invalidate();
        }
        else
        {
            // ���Ͳ����������Ϣ
            MSGSTRUCT msg;
            msg.uMsg = MSG_REFUSEBACK;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
        }
    }
    break;
    case MSG_REFUSEBACK:
    {
        CDialog *pDlg = (CDialog *)AfxGetMainWnd();
        pDlg->MessageBox( _T("�ܱ�Ǹ���Է��ܾ������Ļ�������"), _T("����"), MB_ICONINFORMATION );
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
        // ����1�����ܻ���
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
        RestoreWait();
        Invalidate();
    }
    break;
    case MSG_DRAW:
    {
        if ( IDYES == GetParent()->MessageBox( _T("�Է�������壬�������������"),
                                               _T("����"), MB_ICONQUESTION | MB_YESNO ) )
        {
            CFiveApp *pApp = (CFiveApp *)AfxGetApp();
            pApp->m_nDraw++;
            // �������������Ϣ
            MSGSTRUCT msg;
            msg.uMsg = MSG_AGREEDRAW;
            m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
            // ����󣬽��ð�ť������
            CDialog *pDlg = (CDialog *)GetParent();
            pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
            pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
            SetWait( TRUE );
            // ʹ�����桱�˵���Ч
            pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
        }
        else
        {
            // ���;ܾ�������Ϣ
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
        pDlg->MessageBox( _T("�������������֣��Է����������ĺ�������"), _T("����"), MB_ICONINFORMATION );
        // �����ʹ�����桱�˵���Ч
        pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
    }
    break;
    case MSG_REFUSEDRAW:
    {
        CDialog *pDlg = (CDialog *)GetParent();
        pDlg->MessageBox( _T("�����Է���������ȡ��ʤ�������Ծܾ������ĺ�������"),
                          _T("����"), MB_ICONINFORMATION );
        // �������ð�ť״̬�����ָ�����״̬
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow();
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow();
        RestoreWait();
    }
    break;
    case MSG_CHAT:
    {
        CString strAdd;
        strAdd.Format( _T("%s ˵��%s\r\n"), m_strAgainst, msgRecv.szMsg );
        CEdit *pEdit = (CEdit *)GetParent()->GetDlgItem( IDC_EDT_CHAT );
        pEdit->SetSel( -1, -1, TRUE );
        pEdit->ReplaceSel( strAdd );
    }
    break;
    case MSG_INFORMATION:
    {
        m_strAgainst = msgRecv.szMsg;
        GetParent()->GetDlgItem( IDC_ST_ENEMY )->SetWindowText( m_strAgainst );

        // �����ֽӵ�������Ϣ�󣬻ط��Լ���������Ϣ
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
        pDlg->MessageBox( _T("�Է��Ѿ�Ͷ�����䣬��ϲ����ս������֮����"), _T("ʤ��"), MB_ICONINFORMATION );
        // ���ø���ť������
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        SetWait( TRUE );
        // ���á����桱Ϊ��
        pDlg->GetMenu()->EnableMenuItem( ID_MENU_PLAYAGAIN, MF_ENABLED | MF_BYCOMMAND );
    }
    break;
    case MSG_PLAYAGAIN:
    {
        CDialog *pDlg = (CDialog *)GetParent();
        if ( IDYES == pDlg->MessageBox( _T("�Է���������δ��������������սһ�֣��������������\n\nѡ���񡱽��Ͽ����������ӡ�"),
                                        _T("��ս"), MB_YESNO | MB_ICONQUESTION ) )
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
            // ���ò˵�״̬
            SetMenuState( TRUE );
            // �������̵ȴ�״̬
            SetWait( TRUE );
            // ������������״̬
            m_bConnected = FALSE;
            // ���������������
            pDlg->SetDlgItemText( IDC_ST_ENEMY, _T("����Ҽ���") );
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
// ��Ϣӳ���
BEGIN_MESSAGE_MAP( CTable, CWnd )
    //{{AFX_MSG_MAP(CTable)
    ON_WM_PAINT()
    ON_WM_LBUTTONUP()
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

//////////////////////////////////////////////////////////////////////////
// ����WM_PAINT��Ϣ
//////////////////////////////////////////////////////////////////////////
void CTable::OnPaint()
{
    CPaintDC dc( this );
    CDC MemDC;
    MemDC.CreateCompatibleDC( &dc );
    // װ������
    CBitmap bmp;
    CPen pen;
    bmp.LoadBitmap( IDB_BMP_QP );
    pen.CreatePen( PS_SOLID, 1, 0xff );
    MemDC.SelectObject( &bmp );
    MemDC.SelectObject( &pen );
    MemDC.SetROP2( R2_NOTXORPEN );
    // �����������ݻ�������
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
    // ����������ӵ�ָʾ����
    if ( NULL != m_pGame && !m_pGame->m_StepList.empty() )
    {
        STEP step = *( m_pGame->m_StepList.begin() );
        MemDC.MoveTo( 11 + 25 * step.x, 83 + 25 * step.y );
        MemDC.LineTo( 36 + 25 * step.x, 83 + 25 * step.y );
        MemDC.LineTo( 36 + 25 * step.x, 108 + 25 * step.y );
        MemDC.LineTo( 11 + 25 * step.x, 108 + 25 * step.y );
        MemDC.LineTo( 11 + 25 * step.x, 83 + 25 * step.y );
    }
    // ��ɻ���
    dc.BitBlt( 0, 0, 395, 472, &MemDC,0, 0, SRCCOPY );
}
//////////////////////////////////////////////////////////////////////////
// �������������Ϣ��Ϊ�������֮��
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
    // �����(0, 0)��(14, 14)��Χ�ڣ��Ҹ�����û�����ӣ��������ڴˣ����������沢�˳�����
    if ( x < 0 || x > 14 || y < 0 || y > 14 || m_data[x][y] != -1 )
    {
        MessageBeep( MB_OK );
        return;
    }
    else
    {
        // ���λ�úϷ���������
        SetData( x, y, m_color );
        stepPut.color = m_color;
        stepPut.x = x;
        stepPut.y = y;
        // ����1�����ܻ���
        GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( m_pGame->m_StepList.size() > 1 );
    }
    // �ж�ʤ�������
    if ( Win( m_color ) )
    {
        CFiveApp *pApp = (CFiveApp *)AfxGetApp();
        pApp->m_nWin++;
        m_pGame->Win( stepPut );
        CDialog *pDlg = (CDialog *)GetParent();
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_WIN ), NULL, SND_SYNC | SND_RESOURCE );
        pDlg->MessageBox( _T("��ϲ���������ʤ����"), _T("ʤ��"), MB_ICONINFORMATION );
        pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
        pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
        m_bWait = TRUE;
        return;
    }
    else
    {
        // ��ʼ�ȴ�
        m_bWait = TRUE;
        // ����������Ϣ
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_PUT ), NULL, SND_SYNC | SND_RESOURCE );
        m_pGame->SendStep( stepPut );
    }
}
//////////////////////////////////////////////////////////////////////////
// ����������ǰ�ĵȴ���־
//////////////////////////////////////////////////////////////////////////
void CTable::RestoreWait()
{
    SetWait( m_bOldWait );
}
