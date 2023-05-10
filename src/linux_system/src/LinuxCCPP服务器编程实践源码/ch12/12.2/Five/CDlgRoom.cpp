// CDlgRoom.cpp: 实现文件
//

#include "stdafx.h"
#include "Five.h"
#include "CDlgRoom.h"
#include "afxdialogex.h"
#include "cmd.h"


extern CFiveApp theApp;
// CDlgRoom 对话框
void GetItem(char str[], char item1[], const char * split )//获取第n个逗号后面和n+1逗号前面的字符串
{
    //const char * split = "(";
    char * p;
    p = strtok(str, split);
    int i = 0;
    while (p != NULL)
    {
        printf("%s\n", p);
        if (i == 1)
        {
            sprintf(item1, p);
            break;
        }
        i++;
        p = strtok(NULL, split);
    }
}
IMPLEMENT_DYNAMIC(CDlgRoom, CDialogEx)

CDlgRoom::CDlgRoom(CWnd* pParent /*=nullptr*/)
    : CDialogEx(IDD_ROOM, pParent)
{

}

CDlgRoom::~CDlgRoom()
{
}

void CDlgRoom::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Control(pDX, IDC_LIST1, m_lst);
}


BEGIN_MESSAGE_MAP(CDlgRoom, CDialogEx)
    ON_BN_CLICKED(IDC_BUTTON_CREATE, &CDlgRoom::OnBnClickedButtonCreate)
    ON_BN_CLICKED(IDC_BUTTON_ADD, &CDlgRoom::OnBnClickedButtonAdd)
END_MESSAGE_MAP()


// CDlgRoom 消息处理程序

void CDlgRoom::setOK()
{
    OnOK();
    theApp.m_clinetsock.m_pDlg = NULL;

}
void CDlgRoom::OnBnClickedButtonCreate()
{
    // TODO: 在此添加控件通知处理程序代码
    CString  strInfo;
    int len;
    UpdateData();


    strInfo.Format(_T("%c,%s,%s"), CL_CMD_CREATE, theApp.m_strName,theApp.m_szMyIPAsCreator);//m_strName创建棋局
    len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));

}


void CDlgRoom::OnBnClickedButtonAdd()
{
    // TODO: 在此添加控件通知处理程序代码
    CString strAll, strInfo;


    int len,nSel = m_lst.GetCurSel();
    if (nSel < 0)
    {
        AfxMessageBox("请先选择要加入到棋局！");
        return;
    }

    m_lst.GetText(nSel, strAll);
    GetItem((char*)(LPCTSTR)strAll, theApp.m_szCreatorIPAsJoin,"(");
    theApp.m_szCreatorIPAsJoin[strlen(theApp.m_szCreatorIPAsJoin) - 1] = '\0';
    theApp.m_isCreator = 0;
    theApp.m_pDlgLogin->setOK();
    theApp.m_pDlgLogin = NULL;
    setOK();




}


BOOL CDlgRoom::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    // TODO:  在此添加额外的初始化
    //向服务器获取在线棋盘列表
    CString  strInfo;
    int len;


    strInfo.Format(_T("%c,"), CL_CMD_GET_TABLE_LIST);
    len = theApp.m_clinetsock.Send(strInfo.GetBuffer(strInfo.GetLength()), 2 * strInfo.GetLength());
    if (SOCKET_ERROR == len)
        AfxMessageBox(_T("发送错误"));

    return TRUE;  // return TRUE unless you set the focus to a control
    // 异常: OCX 属性页应返回 FALSE
}
