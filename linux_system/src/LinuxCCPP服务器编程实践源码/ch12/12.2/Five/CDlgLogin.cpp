// CDlgLogin.cpp: 实现文件
//

#include "stdafx.h"
#include "Five.h"
#include "CDlgLogin.h"
#include "afxdialogex.h"
#include "cmd.h"

extern CFiveApp theApp;

int gbcon = 0;//标记是否已经连接服务器

// CDlgLogin 对话框

IMPLEMENT_DYNAMIC(CDlgLogin, CDialogEx)

CDlgLogin::CDlgLogin(CWnd* pParent /*=nullptr*/)
    : CDialogEx(IDD_LOGIN, pParent)
    , m_nServPort(0)
    , m_strName(_T(""))
{



}

CDlgLogin::~CDlgLogin()
{
}

void CDlgLogin::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Control(pDX, IDC_IPADDRESS1, m_ip);
    DDX_Text(pDX, IDC_EDIT1, m_nServPort);
    DDX_Text(pDX, IDC_EDIT2, m_strName);
    DDX_Control(pDX, IDC_EDIT1, m_port);
    DDX_Control(pDX, IDC_EDIT2, m_nick);
}


BEGIN_MESSAGE_MAP(CDlgLogin, CDialogEx)
    ON_BN_CLICKED(IDC_BUTTON_LOGIN, &CDlgLogin::OnBnClickedButtonLogin)
    ON_BN_CLICKED(IDC_REG, &CDlgLogin::OnBnClickedReg)
END_MESSAGE_MAP()


// CDlgLogin 消息处理程序


void CDlgLogin::OnBnClickedButtonLogin()
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
        }
    }
    CString strInfo;
    strInfo.Format("%c,%s", CL_CMD_LOGIN, m_strName);
    int len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());

    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));
}


BOOL CDlgLogin::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    // TODO:  在此添加额外的初始化
    CString strIP = "192.168.11.129";
    DWORD dwIP = ntohl(inet_addr(strIP));
    m_ip.SetAddress(dwIP);

    m_port.SetWindowText("8000");
    m_nick.SetWindowText("Tom");

    theApp.m_pDlgLogin = this;

    return TRUE;  // return TRUE unless you set the focus to a control
    // 异常: OCX 属性页应返回 FALSE
}

void CDlgLogin::setOK()
{
    OnOK();

}
void CDlgLogin::OnBnClickedReg()
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
