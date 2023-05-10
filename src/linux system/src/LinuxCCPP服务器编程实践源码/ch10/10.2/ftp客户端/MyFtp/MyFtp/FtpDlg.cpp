//created by zww
// FtpDlg.cpp : implementation file
//

#include "stdafx.h"
#include "MyFtp.h"
#include "FtpDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CFtpDlg dialog


CFtpDlg::CFtpDlg(CWnd* pParent /*=NULL*/)
    : CDialog(CFtpDlg::IDD, pParent)
{
    //{{AFX_DATA_INIT(CFtpDlg)
    // NOTE: the ClassWizard will add member initialization here
    m_pConnection = NULL;
    m_pFileFind = NULL;
    //}}AFX_DATA_INIT
}


void CFtpDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    //{{AFX_DATA_MAP(CFtpDlg)
    DDX_Control(pDX, IDC_DELETE, m_BtnDelete);
    DDX_Control(pDX, IDC_RENAME, m_BtnRename);
    DDX_Control(pDX, IDC_QUARY, m_BtnQuery);
    DDX_Control(pDX, IDC_UPLOAD, m_BtnUpLoad);
    DDX_Control(pDX, IDC_DOWNLOAD, m_BtnDownLoad);
    DDX_Control(pDX, IDC_LIST_FILE, m_FtpFile);
    //}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CFtpDlg, CDialog)
//{{AFX_MSG_MAP(CFtpDlg)
    ON_BN_CLICKED(IDC_QUARY, OnQuary)
    ON_BN_CLICKED(IDC_EXIT, OnExit)
    ON_BN_CLICKED(IDC_DOWNLOAD, OnDownload)
    ON_BN_CLICKED(IDC_UPLOAD, OnUpload)
    ON_BN_CLICKED(IDC_RENAME, OnRename)
    ON_BN_CLICKED(IDC_DELETE, OnDelete)
    ON_BN_CLICKED(IDC_NEXTDIRECTORY, OnNextdirectory)
    ON_BN_CLICKED(IDC_LASTDIRECTORY, OnLastdirectory)
    ON_NOTIFY(NM_DBLCLK, IDC_LIST_FILE, OnDblclkListFile)
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CFtpDlg message handlers



BOOL CFtpDlg::OnInitDialog()
{
    CDialog::OnInitDialog();

    // TODO: Add extra initialization here

    //����CListCtrl���������
    m_FtpFile.SetExtendedStyle(LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);

    //m_FtpFile.SetBkColor(RGB(22,100,100));

    m_FtpFile.InsertColumn(0,"�ļ���",LVCFMT_CENTER,200);
    m_FtpFile.InsertColumn(1,"����",LVCFMT_CENTER,100);
    m_FtpFile.InsertColumn(2,"�ֽ���",LVCFMT_CENTER,100);

    m_pFileFind = new CFtpFileFind(m_pConnection);

    OnQuary();
    return TRUE;
    // return TRUE unless you set the focus to a control
    // EXCEPTION: OCX Property Pages should return FALSE
}

//�õ���������ǰĿ¼���ļ��б�
void CFtpDlg::OnQuary()
{
    ListContent("*");
}

//������ʾ��ǰĿ¼�����е���Ŀ¼���ļ�
void CFtpDlg::ListContent(LPCTSTR DirName)
{
    m_FtpFile.DeleteAllItems();
    BOOL bContinue;
    bContinue=m_pFileFind->FindFile(DirName);
    if (!bContinue)
    {
        //�������,ʧ��
        m_pFileFind->Close();
        m_pFileFind=NULL;
    }

    CString strFileName;
    CString strFileTime;
    CString strFileLength;

    while (bContinue)
    {
        bContinue = m_pFileFind->FindNextFile();

        strFileName = m_pFileFind->GetFileName(); //�õ��ļ���
        //�õ��ļ����һ���޸ĵ�ʱ��
        FILETIME ft;
        m_pFileFind->GetLastWriteTime(&ft);
        CTime FileTime(ft);
        strFileTime = FileTime.Format("%y/%m/%d");

        if (m_pFileFind->IsDirectory())
        {
            //�����Ŀ¼�����С,��<DIR>����
            strFileLength = "<DIR>";
        }
        else
        {
            //�õ��ļ���С
            if (m_pFileFind->GetLength() <1024)
            {
                strFileLength.Format("%d B",m_pFileFind->GetLength());
            }
            else
            {
                if (m_pFileFind->GetLength() < (1024*1024))
                    strFileLength.Format("%3.3f KB",
                                         (LONGLONG)m_pFileFind->GetLength()/1024.0);
                else
                {
                    if   (m_pFileFind->GetLength()<(1024*1024*1024))
                        strFileLength.Format("%3.3f MB",
                                             (LONGLONG)m_pFileFind->GetLength()/(1024*1024.0));
                    else
                        strFileLength.Format("%1.3f GB",
                                             (LONGLONG)m_pFileFind->GetLength()/(1024.0*1024*1024));
                }
            }
        }
        int i=0;
        m_FtpFile.InsertItem(i,strFileName,0);
        m_FtpFile.SetItemText(i,1,strFileTime);
        m_FtpFile.SetItemText(i,2,strFileLength);
        i++;
    }
}


void CFtpDlg::OnDownload()
{
    // TODO: Add your control notification handler code here
    //����һ�㰴ť
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    if (i==-1)
    {
        AfxMessageBox("û��ѡ���ļ�!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        CString strType=m_FtpFile.GetItemText(i,2);   //�õ�ѡ���������
        if (strType!="<DIR>")   //ѡ������ļ�
        {
            CString strDestName;
            CString strSourceName;
            strSourceName = m_FtpFile.GetItemText(i,0);//�õ���Ҫ���ص��ļ���

            CFileDialog dlg(FALSE,"",strSourceName);

            if (dlg.DoModal()==IDOK)
            {
                //��������ļ��ڱ��ػ��ϴ洢��·��������
                strDestName=dlg.GetPathName();

                //����CFtpConnect���е�GetFile���������ļ�
                if (m_pConnection->GetFile(strSourceName,strDestName))
                    AfxMessageBox("���سɹ���",MB_OK|MB_ICONINFORMATION);
                else
                    AfxMessageBox("����ʧ�ܣ�",MB_OK|MB_ICONSTOP);
            }
        }
        else
        {
            //ѡ�����Ŀ¼
            AfxMessageBox("��������Ŀ¼!\n����ѡ!",MB_OK|MB_ICONSTOP);
        }
    }
    //	MessageBox(str);
}


void CFtpDlg::OnUpload()
{
    // TODO: Add your control notification handler code here
    //��õ�ǰ����
    //���ò�ѯ��ť
    CString strSourceName;
    CString strDestName;
    CFileDialog dlg(TRUE,"","*.*");
    if (dlg.DoModal()==IDOK)
    {
        //��ô��ϴ��ı��ػ��ļ�·�����ļ���
        strSourceName = dlg.GetPathName();
        strDestName = dlg.GetFileName();

        //����CFtpConnect���е�PutFile�����ϴ��ļ�
        if (m_pConnection->PutFile(strSourceName,strDestName))
            AfxMessageBox("�ϴ��ɹ���",MB_OK|MB_ICONINFORMATION);
        else
            AfxMessageBox("�ϴ�ʧ�ܣ�",MB_OK|MB_ICONSTOP);
    }
    OnQuary();
}



void CFtpDlg::OnRename()
{
    // TODO: Add your control notification handler code here
    CString strNewName;
    CString strOldName;

    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED); //�õ�CListCtrl��ѡ�е���
    if (i==-1)
    {
        AfxMessageBox("û��ѡ���ļ�!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        strOldName = m_FtpFile.GetItemText(i,0);//�õ���ѡ����ļ���
        CNewNameDlg dlg;
        if (dlg.DoModal()==IDOK)
        {
            strNewName=dlg.m_NewFileName;
            if (m_pConnection->Rename(strOldName,strNewName))
                AfxMessageBox("�������ɹ���",MB_OK|MB_ICONINFORMATION);
            else
                AfxMessageBox("�޷���������",MB_OK|MB_ICONSTOP);
        }
    }
    OnQuary();
}
//ɾ��ѡ����ļ�
void CFtpDlg::OnDelete()
{
    // TODO: Add your control notification handler code here
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    if (i==-1)
    {
        AfxMessageBox("û��ѡ���ļ�!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        CString  strFileName;
        strFileName = m_FtpFile.GetItemText(i,0);
        if ("<DIR>"==m_FtpFile.GetItemText(i,2))
        {
            AfxMessageBox("����ɾ��Ŀ¼!",MB_OK | MB_ICONSTOP);
        }
        else
        {
            if (m_pConnection->Remove(strFileName))
                AfxMessageBox("ɾ���ɹ���",MB_OK|MB_ICONINFORMATION);
            else
                AfxMessageBox("�޷�ɾ����",MB_OK|MB_ICONSTOP);
        }
    }
    OnQuary();
}

void CFtpDlg::OnNextdirectory()
{

    static CString  strCurrentDirectory, strSub;

    m_pConnection->GetCurrentDirectory(strCurrentDirectory);
    strCurrentDirectory+="/";

    //�õ���ѡ����ı�
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    strSub = m_FtpFile.GetItemText(i,0);

    if (i==-1)
    {
        AfxMessageBox("û��ѡ��Ŀ¼!",MB_OK | MB_ICONQUESTION);
    }
    else
    {   //�ж��ǲ���Ŀ¼
        if ("<DIR>"!=m_FtpFile.GetItemText(i,2))
        {
            AfxMessageBox("������Ŀ¼!",MB_OK | MB_ICONSTOP);
        }
        else
        {
            //���õ�ǰĿ¼
            m_pConnection->SetCurrentDirectory(strCurrentDirectory+strSub);
            //�Ե�ǰĿ¼���в�ѯ
            ListContent("*");
        }
    }
}


//������һ��Ŀ¼
void CFtpDlg::OnLastdirectory()
{

    static CString  strCurrentDirectory;

    m_pConnection->GetCurrentDirectory(strCurrentDirectory);

    if (strCurrentDirectory == "/")
    {
        AfxMessageBox("�Ѿ��Ǹ�Ŀ¼��!",MB_OK | MB_ICONSTOP);
    }
    else
    {
        GetLastDiretory(strCurrentDirectory);
        //���õ�ǰĿ¼
        m_pConnection->SetCurrentDirectory(strCurrentDirectory);
        //�Ե�ǰĿ¼���в�ѯ
        ListContent("*");
    }
}
//һ���ߺ���,���ڵõ���һ��Ŀ¼���ַ�����ʾ
void CFtpDlg::GetLastDiretory(CString &str)
{
    int LastIndex=0;
    for (int i=0; i<str.GetLength(); i++)
    {
        if (str.GetAt(i)=='/')
            LastIndex = i;
    }
    str = str.Left(LastIndex);
    if (LastIndex == 0)
        str="/";
}



//��˫����ʱ��,������һ��Ŀ¼����,���ļ���������
void CFtpDlg::OnDblclkListFile(NMHDR* pNMHDR, LRESULT* pResult)
{
    // TODO: Add your control notification handler code here
    OnNextdirectory();
    *pResult = 0;
}
//�˳��Ի�����Ӧ����
void CFtpDlg::OnExit()
{
    // TODO: Add your control notification handler code here
    m_pConnection = NULL;
    m_pFileFind = NULL;
    DestroyWindow();
}
