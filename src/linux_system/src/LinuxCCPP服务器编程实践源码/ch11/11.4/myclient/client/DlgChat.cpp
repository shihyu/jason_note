// DlgChat.cpp : 实现文件
//

#include "stdafx.h"
#include "client.h"
#include "DlgChat.h"
#include "afxdialogex.h"


// CDlgChat 对话框
#define CL_CMD_CHAT 'c'


IMPLEMENT_DYNAMIC(CDlgChat, CDialogEx)

CDlgChat::CDlgChat(CWnd* pParent /*=NULL*/)
    : CDialogEx(CDlgChat::IDD, pParent)
    , m_strSendContent(_T(""))
{

}

CDlgChat::~CDlgChat()
{
}

void CDlgChat::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Control(pDX, IDC_LIST1, m_lst);
    DDX_Text(pDX, IDC_EDIT2, m_strSendContent);
}


BEGIN_MESSAGE_MAP(CDlgChat, CDialogEx)
    ON_BN_CLICKED(IDC_BUTTON1, &CDlgChat::OnBnClickedButton1)
END_MESSAGE_MAP()


// CDlgChat 消息处理程序


void CDlgChat::OnBnClickedButton1()
{
    // TODO:  在此添加控件通知处理程序代码
    CString  strInfo;
    int len;
    UpdateData();

    if (m_strSendContent.IsEmpty())
        AfxMessageBox(_T("发送内容不能为空"));
    else
    {
        strInfo.Format(_T("%c,%s说:%s"),CL_CMD_CHAT, theApp.m_strName, m_strSendContent);
        len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
        if (SOCKET_ERROR == len)
            AfxMessageBox(_T("发送错误"));
    }
}
