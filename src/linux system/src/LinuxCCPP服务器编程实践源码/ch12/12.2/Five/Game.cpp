//zww
#include "StdAfx.h"
#include "Table.h"
#include "Game.h"
#include "Messages.h"
#include "Resource.h"

//////////////////////////////////////////////////////////////////////////
// CGame���ʵ�ֲ���
//////////////////////////////////////////////////////////////////////////
CGame::~CGame()
{
}
void CGame::Win( const STEP& stepSend )
{
}
//////////////////////////////////////////////////////////////////////////
// COneGame���ʵ�ֲ���
//////////////////////////////////////////////////////////////////////////
COneGame::~COneGame()
{
}
void COneGame::Init()
{
    // ������������״̬
    m_pTable->m_bConnected = FALSE;
    // ���õ�������
    m_pTable->GetParent()->SetDlgItemText( IDC_ST_ENEMY, _T("�����") );
    // �����ʤ������
    int i, j, k, nCount = 0;
    for ( i = 0; i < 15; i++ )
    {
        for ( j = 0; j < 15; j++ )
        {
            for ( k = 0; k < 572; k++ )
            {
                m_Player[i][j][k] = false;
                m_Computer[i][j][k] = false;
            }
        }
    }
    for ( i = 0; i < 2; i++ )
    {
        for ( j = 0; j < 572; j++ )
        {
            m_Win[i][j] = 0;
        }
    }
    for ( i = 0; i < 15; i++ )
    {
        for ( j = 0; j < 11; j++ )
        {
            for ( k = 0; k < 5; k++ )
            {
                m_Player[j + k][i][nCount] = true;
                m_Computer[j + k][i][nCount] = true;
            }
            nCount++;
        }
    }
    for ( i = 0; i < 15; i++ )
    {
        for ( j = 0; j < 11; j++ )
        {
            for ( k = 0; k < 5; k++ )
            {
                m_Player[i][j + k][nCount] = true;
                m_Computer[i][j + k][nCount] = true;
            }
            nCount++;
        }
    }
    for ( i = 0; i < 11; i++ )
    {
        for ( j = 0; j < 11; j++ )
        {
            for ( k = 0; k < 5; k++ )
            {
                m_Player[j + k][i + k][nCount] = true;
                m_Computer[j + k][i + k][nCount] = true;
            }
            nCount++;
        }
    }
    for ( i = 0; i < 11; i++ )
    {
        for ( j = 14; j >= 4; j-- )
        {
            for ( k = 0; k < 5; k++ )
            {
                m_Player[j - k][i + k][nCount] = true;
                m_Computer[j - k][i + k][nCount] = true;
            }
            nCount++;
        }
    }
    if ( 1 == m_pTable->GetColor() )
    {
        // �����Һ��ߣ����ֶ����Ƶ���ռ����Ԫ
        m_pTable->SetData( 7, 7, 0 );
        PlaySound( MAKEINTRESOURCE( IDR_WAVE_PUT ), NULL, SND_RESOURCE | SND_SYNC );
        m_bStart = false;
        for ( i = 0; i < 572; i++ )
        {
            // ������ǰ���ݣ�������֮��
            m_nOldWin[0][i] = m_Win[0][i];
            m_nOldWin[1][i] = m_Win[1][i];
            m_bOldPlayer[i] = m_Player[7][7][i];
        }
        for ( i = 0; i < 572; i++ )
        {
            // �޸ļ�������Ӻ����̵ı仯״��
            if ( m_Computer[7][7][i] && m_Win[1][i] != -1 )
            {
                m_Win[1][i]++;
            }
            if ( m_Player[7][7][i] )
            {
                m_Player[7][7][i] = false;
                m_Win[0][i] = -1;
            }
        }
    }
    else
    {
        m_bStart = true;
    }
}
void COneGame::SendStep( const STEP& stepPut )
{
    int bestx, besty, i, j, pi, pj, ptemp, ctemp, pscore = 10, cscore = -10000;
    int ctempTable[15][15], ptempTable[15][15];
    int m, n, temp1[20], temp2[20]; // �ݴ��һ����������Ϣ

    m_pTable->GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    // ������ǰ���ݣ�������֮��
    for ( i = 0; i < 572; i++)
    {
        m_nOldWin[0][i] = m_Win[0][i];
        m_nOldWin[1][i] = m_Win[1][i];
        m_bOldPlayer[i] = m_Player[stepPut.x][stepPut.y][i];
        m_bOldComputer[i] = m_Computer[stepPut.x][stepPut.y][i];
    }
    // �޸�������Ӻ�����״̬�ı仯
    for ( i = 0; i < 572; i++ )
    {
        // �޸�״̬�仯
        if ( m_Player[stepPut.x][stepPut.y][i] && m_Win[0][i] != -1 )
            m_Win[0][i]++;
        if ( m_Computer[stepPut.x][stepPut.y][i] )
        {
            m_Computer[stepPut.x][stepPut.y][i] = false;
            m_Win[1][i] = -1;
        }
    }
    if ( m_bStart )
    {
        // �ֶ�ȷ����һ������Ԫ��(8, 8)
        if ( -1 == m_pTable->m_data[7][7] )
        {
            bestx = 7;
            besty = 7;
        }
        else
        {
            bestx = 8;
            besty = 8;
        }
        m_bStart = false;
    }
    else
    {
        STEP step;
        // Ѱ�����λ��
        GetTable( ctempTable, m_pTable->m_data );
        while ( SearchBlank( i, j, ctempTable ) )
        {
            n = 0;
            pscore = 10;
            GetTable( ptempTable, m_pTable->m_data );
            ctempTable[i][j] = 2; // ����ѱ�����
            step.color = 1 - m_pTable->GetColor();
            step.x = i;
            step.y = j;
            // �������λ���
            ctemp = GiveScore( step );
            for ( m = 0; m < 572; m++ )
            {
                // ��ʱ���������Ϣ
                if ( m_Player[i][j][m] )
                {
                    temp1[n] = m;
                    m_Player[i][j][m] = false;
                    temp2[n] = m_Win[0][m];
                    m_Win[0][m] = -1;
                    n++;
                }
            }
            ptempTable[i][j] = 0;

            pi = i;
            pj = j;
            while ( SearchBlank( i, j, ptempTable ) )
            {

                ptempTable[i][j] = 2; // ����ѱ�����
                step.color = m_pTable->GetColor();
                step.x = i;
                step.y = j;
                ptemp = GiveScore( step );
                if ( pscore > ptemp ) // ��ʱΪ������ӣ����ü�С����ʱӦѡȡ��Сֵ
                    pscore = ptemp;
            }
            for ( m = 0; m < n; m++ )
            {
                // �ָ������Ϣ
                m_Player[pi][pj][temp1[m]] = true;
                m_Win[0][temp1[m]] = temp2[m];
            }
            if ( ctemp + pscore > cscore ) // ��ʱΪ��������ӣ����ü�С����ʱӦѡȡ�����ֵ
            {
                cscore = ctemp + pscore;
                bestx = pi;
                besty = pj;
            }
        }
    }
    m_step.color = 1 - m_pTable->GetColor();
    m_step.x = bestx;
    m_step.y = besty;
    for ( i = 0; i < 572; i++ )
    {
        // �޸ļ�������Ӻ����̵ı仯״��
        if ( m_Computer[bestx][besty][i] && m_Win[1][i] != -1 )
            m_Win[1][i]++;
        if ( m_Player[bestx][besty][i] )
        {
            m_Player[bestx][besty][i] = false;
            m_Win[0][i] = -1;
        }
    }
    m_pTable->GetParent()->GetDlgItem( IDC_BTN_BACK )->EnableWindow();
    // �����ǵ�����Ϸ������ֱ�ӽ�������
    m_pTable->Receive();
}
void COneGame::ReceiveMsg( MSGSTRUCT *pMsg )
{
    pMsg->color = m_step.color;
    pMsg->x = m_step.x;
    pMsg->y = m_step.y;
    pMsg->uMsg = MSG_PUTSTEP;
}
void COneGame::Back()
{
    int i;
    // ������Ϸֱ���������
    STEP step;
    // �ڵ�һ�����������ӣ�
    step = *( m_StepList.begin() );
    m_StepList.pop_front();
    m_pTable->m_data[step.x][step.y] = -1;
    // �ָ�ԭ��ʤ������
    for ( i = 0; i < 572; i++ )
    {
        m_Win[0][i] = m_nOldWin[0][i];
        m_Win[1][i] = m_nOldWin[1][i];
        m_Player[step.x][step.y][i] = m_bOldPlayer[i];
    }
    // �ڵڶ�����������ӣ�
    step = *( m_StepList.begin() );
    m_StepList.pop_front();
    m_pTable->m_data[step.x][step.y] = -1;
    // �ָ�ԭ��ʤ������
    for ( i = 0; i < 572; i++ )
    {
        m_Computer[step.x][step.y][i] = m_bOldComputer[i];
    }
    m_pTable->Invalidate();
    // ���ǵ�����ĸ��ɣ���ʱ��Ͳ����������
    AfxGetMainWnd()->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
}
int COneGame::GiveScore( const STEP& stepPut )
{
    int i, nScore = 0;
    for ( i = 0; i < 572; i++ )
    {
        if ( m_pTable->GetColor() == stepPut.color )
        {
            // �����
            if ( m_Player[stepPut.x][stepPut.y][i] )
            {
                switch ( m_Win[0][i] )
                {
                case 1:
                    nScore -= 5;
                    break;
                case 2:
                    nScore -= 50;
                    break;
                case 3:
                    nScore -= 500;
                    break;
                case 4:
                    nScore -= 5000;
                    break;
                default:
                    break;
                }
            }
        }
        else
        {
            // �������
            if ( m_Computer[stepPut.x][stepPut.y][i] )
            {
                switch ( m_Win[1][i] )
                {
                case 1:
                    nScore += 5;
                    break;
                case 2:
                    nScore += 50;
                    break;
                case 3:
                    nScore += 100;
                    break;
                case 4:
                    nScore += 10000;
                    break;
                default:
                    break;
                }
            }
        }
    }
    return nScore;
}
void COneGame::GetTable( int tempTable[][15], int nowTable[][15] )
{
    int i, j;
    for ( i = 0; i < 15; i++ )
    {
        for ( j = 0; j < 15; j++ )
        {
            tempTable[i][j] = nowTable[i][j];
        }
    }
}
bool COneGame::SearchBlank( int &i, int &j, int nowTable[][15] )
{
    int x, y;
    for ( x = 0; x < 15; x++ )
    {
        for ( y = 0; y < 15; y++ )
        {
            if ( nowTable[x][y] == -1 && nowTable[x][y] != 2 )
            {
                i = x;
                j = y;
                return true;
            }
        }
    }
    return false;
}
//////////////////////////////////////////////////////////////////////////
// CTwoGame���ʵ�ֲ���
//////////////////////////////////////////////////////////////////////////
CTwoGame::~CTwoGame()
{
}
//////////////////////////////////////////////////////////////////////////
void CTwoGame::Init()
{
}
void CTwoGame::Win( const STEP& stepSend )
{
    SendStep( stepSend );
}
void CTwoGame::SendStep( const STEP& stepPut )
{
    MSGSTRUCT msg;
    msg.uMsg = MSG_PUTSTEP;
    msg.color = stepPut.color;
    msg.x = stepPut.x;
    msg.y = stepPut.y;

    m_pTable->m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
void CTwoGame::ReceiveMsg( MSGSTRUCT *pMsg )
{
    int nRet = m_pTable->m_conn.Receive( pMsg, sizeof( MSGSTRUCT ) );
    if ( SOCKET_ERROR == nRet )
    {
        AfxGetMainWnd()->MessageBox( _T("��������ʱ�����������������������ӡ�"), _T("����"), MB_ICONSTOP );
    }
}
void CTwoGame::Back()
{
    CDialog *pDlg = (CDialog *)AfxGetMainWnd();
    // ʹ��ťʧЧ
    pDlg->GetDlgItem( IDC_BTN_BACK )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_HQ )->EnableWindow( FALSE );
    pDlg->GetDlgItem( IDC_BTN_LOST )->EnableWindow( FALSE );
    // ���õȴ���־
    m_pTable->SetWait( TRUE );

    MSGSTRUCT msg;
    msg.uMsg = MSG_BACK;

    m_pTable->m_conn.Send( (LPCVOID)&msg, sizeof( MSGSTRUCT ) );
}
