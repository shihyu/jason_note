//zww
// ClientDlg.cpp : implementation file
//

#include "stdafx.h"
#include "five.h"
#include "Table.h"
#include "ClientDlg.h"
#include "cmd.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CClientDlg dialog
extern CFiveApp theApp;

CClientDlg::CClientDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CClientDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CClientDlg)
    // NOTE: the ClassWizard will add member initialization here
    //}}AFX_DATA_INIT
}


void CClientDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CClientDlg)
    // NOTE: the ClassWizard will add DDX and DDV calls here
    //}}AFX_DATA_MAP
    DDX_Control(pDX, IDC_EDIT_HOST, m_edtHost);
}


BEGIN_MESSAGE_MAP(CClientDlg, CDialog)
    //{{AFX_MSG_MAP(CClientDlg)
    ON_BN_CLICKED(IDC_BTN_OUT, OnBtnOut)
    ON_EN_UPDATE(IDC_EDIT_HOST, OnUpdateEditHost)
    ON_WM_TIMER()
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CClientDlg message handlers

void CClientDlg::OnOK()
{
    // ����OnOK��ʹ���س���ʱ���˳�
}


void CClientDlg::Connect()
{
    // TODO: Add your control notification handler code here
    CString strHost;
    m_edtHost.SetWindowText(theApp.m_szCreatorIPAsJoin);
    // ��ȡ��������
    GetDlgItemText( IDC_EDIT_HOST, strHost );
    // ���ó�ʱʱ��
    m_nTimer = 5;
    // ��ʼ������״̬
    m_pTable->m_bConnected = FALSE;
    // ���ÿؼ���Ч״̬
    GetDlgItem( IDC_BTN_CONNECT )->EnableWindow( FALSE );
    GetDlgItem( IDC_EDIT_HOST )->EnableWindow( FALSE );
    // �����׽��ֲ�����
    m_pTable->m_conn.Create();
    m_pTable->m_conn.Connect( strHost, 20000 );
    // ��ʼ��ʱ
    SetTimer( 1, 1000, NULL );
}

void CClientDlg::OnBtnOut()
{
    // TODO: Add your control notification handler code here
    KillTimer( 1 );
    OnCancel();
}

void CClientDlg::OnUpdateEditHost()
{
    // TODO: If this is a RICHEDIT control, the control will not
    // send this notification unless you override the CDialog::OnInitDialog()
    // function to send the EM_SETEVENTMASK message to the control
    // with the ENM_UPDATE flag ORed into the lParam mask.

    // TODO: Add your control notification handler code here
    // ���������������ʹ�����ӡ���ťʧЧ
    CString str;
    GetDlgItemText( IDC_EDIT_HOST, str );
    GetDlgItem( IDC_BTN_CONNECT )->EnableWindow( !str.IsEmpty() );
}

BOOL CClientDlg::OnInitDialog()
{
    CDialog::OnInitDialog();

    // TODO: Add extra initialization here
    SetDlgItemText( IDC_ST_TIMER, _T("") );
    m_pTable = (CTable *)GetParent()->GetDlgItem( IDC_TABLE );

    Connect();

    return TRUE;  // return TRUE unless you set the focus to a control
    // EXCEPTION: OCX Property Pages should return FALSE
}

void CClientDlg::OnTimer(UINT nIDEvent)
{
    // TODO: Add your message handler code here and/or call default
    if ( 1 == nIDEvent )
    {
        if ( m_pTable->m_bConnected )
        {
            KillTimer( 1 );
            EndDialog( IDOK );
        }
        else if ( 0 == m_nTimer )
        {
            KillTimer( 1 );
            MessageBox( _T("���ӶԷ�ʧ�ܣ�������������IP��ַ�Ƿ���ȷ���Լ����������Ƿ�������"),
                        _T("����ʧ��"), MB_ICONERROR );
            SetDlgItemText( IDC_ST_TIMER, _T("") );
            GetDlgItem( IDC_EDIT_HOST )->EnableWindow();
            SetDlgItemText( IDC_EDIT_HOST, _T("") );
            GetDlgItem( IDC_EDIT_HOST )->SetFocus();
        }
        else
        {
            CString str;
            str.Format( _T("��������...(%d)"), m_nTimer-- );
            SetDlgItemText( IDC_ST_TIMER, str);
        }
    }
    CDialog::OnTimer(nIDEvent);
}
