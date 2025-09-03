
// clientDlg.cpp : ʵ���ļ�
//

#include "stdafx.h"
#include "client.h"
#include "clientDlg.h"
#include "afxdialogex.h"
#include "DlgChat.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif

int gbcon = 0;//����Ƿ��Ѿ����ӷ�����
#define CL_CMD_LOGIN 'l'
#define CL_CMD_REG 'r'

// ����Ӧ�ó��򡰹��ڡ��˵���� CAboutDlg �Ի���

class CAboutDlg : public CDialogEx
{
public:
    CAboutDlg();

// �Ի�������
    enum { IDD = IDD_ABOUTBOX };

protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV ֧��

// ʵ��
protected:
    DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CclientDlg �Ի���



CclientDlg::CclientDlg(CWnd* pParent /*=NULL*/)
    : CDialogEx(CclientDlg::IDD, pParent)
    , m_nServPort(0)
    , m_strName(_T(""))
{
    m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CclientDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Text(pDX, IDC_EDIT_NAME, m_strName);
    DDX_Control(pDX, IDC_IPADDRESS1, m_ip);
    DDX_Text(pDX, IDC_EDIT1, m_nServPort);
    DDX_Control(pDX, IDC_EDIT1, m_port);
    DDX_Control(pDX, IDC_EDIT_NAME, m_nick);
}

BEGIN_MESSAGE_MAP(CclientDlg, CDialogEx)
    ON_WM_SYSCOMMAND()
    ON_WM_PAINT()
    ON_WM_QUERYDRAGICON()
    ON_BN_CLICKED(IDC_BUTTON1, &CclientDlg::OnBnClickedButton1)
    ON_BN_CLICKED(IDC_BUTTON_REG, &CclientDlg::OnBnClickedButtonReg)
END_MESSAGE_MAP()


// CclientDlg ��Ϣ�������

BOOL CclientDlg::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    // ��������...���˵�����ӵ�ϵͳ�˵��С�

    // IDM_ABOUTBOX ������ϵͳ���Χ�ڡ�
    ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
    ASSERT(IDM_ABOUTBOX < 0xF000);

    CMenu* pSysMenu = GetSystemMenu(FALSE);
    if (pSysMenu != NULL)
    {
        BOOL bNameValid;
        CString strAboutMenu;
        bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
        ASSERT(bNameValid);
        if (!strAboutMenu.IsEmpty())
        {
            pSysMenu->AppendMenu(MF_SEPARATOR);
            pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
        }
    }

    // ���ô˶Ի����ͼ�ꡣ  ��Ӧ�ó��������ڲ��ǶԻ���ʱ����ܽ��Զ�
    //  ִ�д˲���
    SetIcon(m_hIcon, TRUE);			// ���ô�ͼ��
    SetIcon(m_hIcon, FALSE);		// ����Сͼ��

    // TODO:  �ڴ���Ӷ���ĳ�ʼ������
    CString strIP = "192.168.11.129";
    DWORD dwIP = ntohl(inet_addr(strIP));
    m_ip.SetAddress(dwIP);

    m_port.SetWindowText("8000");
    m_nick.SetWindowText("Tom");


    return TRUE;  // ���ǽ��������õ��ؼ������򷵻� TRUE
}

void CclientDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
    if ((nID & 0xFFF0) == IDM_ABOUTBOX)
    {
        CAboutDlg dlgAbout;
        dlgAbout.DoModal();
    }
    else
    {
        CDialogEx::OnSysCommand(nID, lParam);
    }
}

// �����Ի��������С����ť������Ҫ����Ĵ���
//  �����Ƹ�ͼ�ꡣ  ����ʹ���ĵ�/��ͼģ�͵� MFC Ӧ�ó���
//  �⽫�ɿ���Զ���ɡ�

void CclientDlg::OnPaint()
{
    if (IsIconic())
    {
        CPaintDC dc(this); // ���ڻ��Ƶ��豸������

        SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

        // ʹͼ���ڹ����������о���
        int cxIcon = GetSystemMetrics(SM_CXICON);
        int cyIcon = GetSystemMetrics(SM_CYICON);
        CRect rect;
        GetClientRect(&rect);
        int x = (rect.Width() - cxIcon + 1) / 2;
        int y = (rect.Height() - cyIcon + 1) / 2;

        // ����ͼ��
        dc.DrawIcon(x, y, m_hIcon);
    }
    else
    {
        CDialogEx::OnPaint();
    }
}

//���û��϶���С������ʱϵͳ���ô˺���ȡ�ù��
//��ʾ��
HCURSOR CclientDlg::OnQueryDragIcon()
{
    return static_cast<HCURSOR>(m_hIcon);
}



void CclientDlg::OnBnClickedButton1()
{
    // TODO:  �ڴ���ӿؼ�֪ͨ����������
    CString strIP, strPort;
    UINT port;

    UpdateData();
    if (m_ip.IsBlank() || m_nServPort < 1024 || m_strName.IsEmpty())
    {
        AfxMessageBox(_T("�����÷�������Ϣ"));
        return;
    }
    BYTE nf1, nf2, nf3, nf4;
    m_ip.GetAddress(nf1, nf2, nf3, nf4);
    strIP.Format(_T("%d.%d.%d.%d"), nf1, nf2, nf3, nf4);

    theApp.m_strName = m_strName;

    if (!gbcon)
    {
        if (theApp.m_clinetsock.Connect(strIP, m_nServPort))
        {
            gbcon = 1;
            //AfxMessageBox(_T("���ӷ������ɹ�!"));

        }
        else
        {
            AfxMessageBox(_T("���ӷ�����ʧ��!"));
        }
    }
    CString strInfo;
    strInfo.Format("%c,%s", CL_CMD_LOGIN, m_strName);
    int len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());

    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("���ʹ���"));
}





void CclientDlg::OnBnClickedButtonReg()
{
    // TODO: �ڴ���ӿؼ�֪ͨ����������
    CString strIP, strPort;
    UINT port;

    UpdateData();
    if (m_ip.IsBlank() || m_nServPort < 1024 || m_strName.IsEmpty())
    {
        AfxMessageBox(_T("�����÷�������Ϣ"));
        return;
    }
    BYTE nf1, nf2, nf3, nf4;
    m_ip.GetAddress(nf1, nf2, nf3, nf4);
    strIP.Format(_T("%d.%d.%d.%d"), nf1, nf2, nf3, nf4);

    theApp.m_strName = m_strName;

    if (!gbcon)
    {
        if (theApp.m_clinetsock.Connect(strIP, m_nServPort))
        {
            gbcon = 1;
            //AfxMessageBox(_T("���ӷ������ɹ�!"));
        }
        else
        {
            AfxMessageBox(_T("���ӷ�����ʧ��!"));
            return;
        }
    }
    //-------------ע��---------
    CString strInfo;
    strInfo.Format("%c,%s", CL_CMD_REG, m_strName);
    int len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());

    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("���ʹ���"));
}
