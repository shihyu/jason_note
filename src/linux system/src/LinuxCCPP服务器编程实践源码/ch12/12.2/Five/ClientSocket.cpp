// ClientSocket.cpp : 实现文件
//

#include "stdafx.h"
#include "five.h"
#include "ClientSocket.h"
#include "CDlgRoom.h"
#include "cmd.h"
// CClientSocket
extern CFiveApp theApp;


CClientSocket::CClientSocket()
{
    m_pDlg = NULL;
}

CClientSocket::~CClientSocket()
{
}


// CClientSocket 成员函数
void CClientSocket::SetWnd(CDlgRoom *pDlg)
{
    m_pDlg = pDlg;
}


void GetItem(char str[], char reply[],int n)//获取第n个逗号后面和n+1逗号前面的字符串
{
    const char * split = ",";
    char * p;
    p = strtok(str, split);
    int i = 0;
    while (p != NULL)
    {
        printf("%s\n", p);
        if (i == n)
        {
            sprintf(reply, p);
            break;
        }
        i++;
        p = strtok(NULL, split);
    }
}

int GetName(char str[], char szName[],int n) //n表示第几个分隔符后
{
    //char str[] ="a,b,c,d*e";
    const char * split = ",";
    char * p;
    p = strtok(str, split);
    int i = 0;
    while (p != NULL)
    {
        printf("%s\n", p);
        if (i == n)
        {
            sprintf(szName, p);
            return 0;
        }

        i++;
        p = strtok(NULL, split);
    }
    return -1;
}

void CClientSocket::OnReceive(int nErrorCode)
{
    // TODO:  在此添加专用代码和/或调用基类
    CString str;
    int i = 1,r=0;
    char buffer[2048], rep[128] = "",   szName[64]="";
    if (m_pDlg) //m_pDlg指向大厅对话框
    {
        int len = Receive(buffer, 2048);
        if (len != -1)
        {
            buffer[len] = '\0';
            buffer[len+1] = '\0';

            if (buffer[0] == 'c')// create game reply
            {
                GetName(buffer, szName,2);
                str.Format(_T("GAME created by %s"), szName);
                m_pDlg->m_lst.AddString(str);
                theApp.m_isCreator = 1; //当前用户是游戏创建者
                theApp.m_pDlgLogin->setOK();
                theApp.m_pDlgLogin = NULL;
                m_pDlg->setOK();
                m_pDlg = NULL;

            }
            else if (buffer[0] == 'g')// get all free tables reply
            {
                i = 1;
                m_pDlg->m_lst.ResetContent();
                do
                {
                    r = GetName(buffer, szName, i);
                    if (r == -1)break;
                    m_pDlg->m_lst.AddString(szName);
                } while (1);


            }

        }
    }
    else
    {
        //注册回复
        int len = Receive(buffer, 2048);
        if (len != -1)
        {
            buffer[len] = '\0';
            buffer[len + 1] = '\0';
            str.Format(_T("%s"), buffer);
            if (buffer[0] == 'r')
            {
                GetItem(buffer, rep,1);
                if(strcmp("ok", rep)==0)
                    AfxMessageBox("注册成功");
                else if(strcmp("exist",rep)==0)
                    AfxMessageBox("注册失败，用户名已经存在!");
            }
            else if (buffer[0] == 'l')
            {
                GetItem(buffer, rep,1);
                if (strcmp("noexist", rep) == 0)
                    AfxMessageBox("登录失败，用户名不存在，请先注册.");
                else if (strcmp("hasLogined", rep) == 0) AfxMessageBox("该用户已经登录!");
                else if (strcmp("ok", rep) == 0)
                {
                    AfxMessageBox("登录成功");
                    CDlgRoom dlg;
                    theApp.m_clinetsock.SetWnd(&dlg);

                    dlg.DoModal();
                }
            }
        }
    }
    CSocket::OnReceive(nErrorCode);
}
