
// clientDlg.cpp : 实现文件
//

#include "stdafx.h"
#include "client.h"
#include "clientDlg.h"
#include "afxdialogex.h"
#include "DlgChat.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif

int gbcon = 0;//标记是否已经连接服务器
#define CL_CMD_LOGIN 'l'
#define CL_CMD_REG 'r'

// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialogEx
{
public:
    CAboutDlg();

// 对话框数据
    enum { IDD = IDD_ABOUTBOX };

protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
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


// CclientDlg 对话框



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


// CclientDlg 消息处理程序

BOOL CclientDlg::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    // 将“关于...”菜单项添加到系统菜单中。

    // IDM_ABOUTBOX 必须在系统命令范围内。
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

    // 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
    //  执行此操作
    SetIcon(m_hIcon, TRUE);			// 设置大图标
    SetIcon(m_hIcon, FALSE);		// 设置小图标

    // TODO:  在此添加额外的初始化代码
    CString strIP = "192.168.11.129";
    DWORD dwIP = ntohl(inet_addr(strIP));
    m_ip.SetAddress(dwIP);

    m_port.SetWindowText("8000");
    m_nick.SetWindowText("Tom");


    return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
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

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CclientDlg::OnPaint()
{
    if (IsIconic())
    {
        CPaintDC dc(this); // 用于绘制的设备上下文

        SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

        // 使图标在工作区矩形中居中
        int cxIcon = GetSystemMetrics(SM_CXICON);
        int cyIcon = GetSystemMetrics(SM_CYICON);
        CRect rect;
        GetClientRect(&rect);
        int x = (rect.Width() - cxIcon + 1) / 2;
        int y = (rect.Height() - cyIcon + 1) / 2;

        // 绘制图标
        dc.DrawIcon(x, y, m_hIcon);
    }
    else
    {
        CDialogEx::OnPaint();
    }
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR CclientDlg::OnQueryDragIcon()
{
    return static_cast<HCURSOR>(m_hIcon);
}



void CclientDlg::OnBnClickedButton1()
{
    // TODO:  在此添加控件通知处理程序代码
    CString strIP, strPort;
    UINT port;

    UpdateData();
    if (m_ip.IsBlank() || m_nServPort < 1024 || m_strName.IsEmpty())
    {
        AfxMessageBox(_T("请设置服务器信息"));
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
            //AfxMessageBox(_T("连接服务器成功!"));

        }
        else
        {
            AfxMessageBox(_T("连接服务器失败!"));
        }
    }
    CString strInfo;
    strInfo.Format("%c,%s", CL_CMD_LOGIN, m_strName);
    int len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());

    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));
}





void CclientDlg::OnBnClickedButtonReg()
{
    // TODO: 在此添加控件通知处理程序代码
    CString strIP, strPort;
    UINT port;

    UpdateData();
    if (m_ip.IsBlank() || m_nServPort < 1024 || m_strName.IsEmpty())
    {
        AfxMessageBox(_T("请设置服务器信息"));
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
            //AfxMessageBox(_T("连接服务器成功!"));
        }
        else
        {
            AfxMessageBox(_T("连接服务器失败!"));
            return;
        }
    }
    //-------------注册---------
    CString strInfo;
    strInfo.Format("%c,%s", CL_CMD_REG, m_strName);
    int len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());

    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));
}
