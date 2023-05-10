// ClientSocket.cpp : ʵ���ļ�
//

#include "stdafx.h"
#include "client.h"
#include "ClientSocket.h"


// CClientSocket

CClientSocket::CClientSocket()
{
    m_pDlg = NULL;
}

CClientSocket::~CClientSocket()
{
}


// CClientSocket ��Ա����
void CClientSocket::SetWnd(CDlgChat *pDlg)
{
    m_pDlg = pDlg;
}


void GetReply(char str[], char reply[])
{
    const char * split = ",";
    char * p;
    p = strtok(str, split);
    int i = 0;
    while (p != NULL)
    {
        printf("%s\n", p);
        if (i == 1) sprintf(reply, p);
        i++;
        p = strtok(NULL, split);
    }
}


void CClientSocket::OnReceive(int nErrorCode)
{
    // TODO:  �ڴ����ר�ô����/����û���
    CString str;
    char buffer[2048], rep[128] = "";
    if (m_pDlg) //m_pDlgָ������Ի���
    {

        int len = Receive(buffer, 2048);
        if (len != -1)
        {
            buffer[len] = '\0';
            buffer[len+1] = '\0';
            str.Format(_T("%s"), buffer);
            m_pDlg->m_lst.AddString(str);
        }
    }
    else
    {
        //ע��ظ�
        int len = Receive(buffer, 2048);
        if (len != -1)
        {
            buffer[len] = '\0';
            buffer[len + 1] = '\0';
            str.Format(_T("%s"), buffer);
            if (buffer[0] == 'r')
            {
                GetReply(buffer, rep);
                if(strcmp("ok", rep)==0)
                    AfxMessageBox("ע��ɹ�");
                else if(strcmp("exist",rep)==0)
                    AfxMessageBox("ע��ʧ�ܣ��û����Ѿ�����!");
            }
            else if (buffer[0] == 'l')
            {
                GetReply(buffer, rep);
                if (strcmp("noexist", rep) == 0)
                    AfxMessageBox("��¼ʧ�ܣ��û��������ڣ�����ע��.");
                else if (strcmp("ok", rep) == 0)
                {
                    AfxMessageBox("��¼�ɹ�");
                    CDlgChat dlg;
                    theApp.m_clinetsock.SetWnd(&dlg);
                    dlg.DoModal();
                }
            }
        }
    }
    CSocket::OnReceive(nErrorCode);
}
