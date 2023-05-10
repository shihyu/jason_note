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

    //设置CListCtrl对象的属性
    m_FtpFile.SetExtendedStyle(LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);

    //m_FtpFile.SetBkColor(RGB(22,100,100));

    m_FtpFile.InsertColumn(0,"文件名",LVCFMT_CENTER,200);
    m_FtpFile.InsertColumn(1,"日期",LVCFMT_CENTER,100);
    m_FtpFile.InsertColumn(2,"字节数",LVCFMT_CENTER,100);

    m_pFileFind = new CFtpFileFind(m_pConnection);

    OnQuary();
    return TRUE;
    // return TRUE unless you set the focus to a control
    // EXCEPTION: OCX Property Pages should return FALSE
}

//得到服务器当前目录的文件列表
void CFtpDlg::OnQuary()
{
    ListContent("*");
}

//用于显示当前目录下所有的子目录与文件
void CFtpDlg::ListContent(LPCTSTR DirName)
{
    m_FtpFile.DeleteAllItems();
    BOOL bContinue;
    bContinue=m_pFileFind->FindFile(DirName);
    if (!bContinue)
    {
        //查找完毕,失败
        m_pFileFind->Close();
        m_pFileFind=NULL;
    }

    CString strFileName;
    CString strFileTime;
    CString strFileLength;

    while (bContinue)
    {
        bContinue = m_pFileFind->FindNextFile();

        strFileName = m_pFileFind->GetFileName(); //得到文件名
        //得到文件最后一次修改的时间
        FILETIME ft;
        m_pFileFind->GetLastWriteTime(&ft);
        CTime FileTime(ft);
        strFileTime = FileTime.Format("%y/%m/%d");

        if (m_pFileFind->IsDirectory())
        {
            //如果是目录不求大小,用<DIR>代替
            strFileLength = "<DIR>";
        }
        else
        {
            //得到文件大小
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
    //禁用一点按钮
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    if (i==-1)
    {
        AfxMessageBox("没有选择文件!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        CString strType=m_FtpFile.GetItemText(i,2);   //得到选择项的类型
        if (strType!="<DIR>")   //选择的是文件
        {
            CString strDestName;
            CString strSourceName;
            strSourceName = m_FtpFile.GetItemText(i,0);//得到所要下载的文件名

            CFileDialog dlg(FALSE,"",strSourceName);

            if (dlg.DoModal()==IDOK)
            {
                //获得下载文件在本地机上存储的路径和名称
                strDestName=dlg.GetPathName();

                //调用CFtpConnect类中的GetFile函数下载文件
                if (m_pConnection->GetFile(strSourceName,strDestName))
                    AfxMessageBox("下载成功！",MB_OK|MB_ICONINFORMATION);
                else
                    AfxMessageBox("下载失败！",MB_OK|MB_ICONSTOP);
            }
        }
        else
        {
            //选择的是目录
            AfxMessageBox("不能下载目录!\n请重选!",MB_OK|MB_ICONSTOP);
        }
    }
    //	MessageBox(str);
}


void CFtpDlg::OnUpload()
{
    // TODO: Add your control notification handler code here
    //获得当前输入
    //禁用查询按钮
    CString strSourceName;
    CString strDestName;
    CFileDialog dlg(TRUE,"","*.*");
    if (dlg.DoModal()==IDOK)
    {
        //获得待上传的本地机文件路径和文件名
        strSourceName = dlg.GetPathName();
        strDestName = dlg.GetFileName();

        //调用CFtpConnect类中的PutFile函数上传文件
        if (m_pConnection->PutFile(strSourceName,strDestName))
            AfxMessageBox("上传成功！",MB_OK|MB_ICONINFORMATION);
        else
            AfxMessageBox("上传失败！",MB_OK|MB_ICONSTOP);
    }
    OnQuary();
}



void CFtpDlg::OnRename()
{
    // TODO: Add your control notification handler code here
    CString strNewName;
    CString strOldName;

    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED); //得到CListCtrl被选中的项
    if (i==-1)
    {
        AfxMessageBox("没有选择文件!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        strOldName = m_FtpFile.GetItemText(i,0);//得到所选择的文件名
        CNewNameDlg dlg;
        if (dlg.DoModal()==IDOK)
        {
            strNewName=dlg.m_NewFileName;
            if (m_pConnection->Rename(strOldName,strNewName))
                AfxMessageBox("重命名成功！",MB_OK|MB_ICONINFORMATION);
            else
                AfxMessageBox("无法重命名！",MB_OK|MB_ICONSTOP);
        }
    }
    OnQuary();
}
//删除选择的文件
void CFtpDlg::OnDelete()
{
    // TODO: Add your control notification handler code here
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    if (i==-1)
    {
        AfxMessageBox("没有选择文件!",MB_OK | MB_ICONQUESTION);
    }
    else
    {
        CString  strFileName;
        strFileName = m_FtpFile.GetItemText(i,0);
        if ("<DIR>"==m_FtpFile.GetItemText(i,2))
        {
            AfxMessageBox("不能删除目录!",MB_OK | MB_ICONSTOP);
        }
        else
        {
            if (m_pConnection->Remove(strFileName))
                AfxMessageBox("删除成功！",MB_OK|MB_ICONINFORMATION);
            else
                AfxMessageBox("无法删除！",MB_OK|MB_ICONSTOP);
        }
    }
    OnQuary();
}

void CFtpDlg::OnNextdirectory()
{

    static CString  strCurrentDirectory, strSub;

    m_pConnection->GetCurrentDirectory(strCurrentDirectory);
    strCurrentDirectory+="/";

    //得到所选择的文本
    int i=m_FtpFile.GetNextItem(-1,LVNI_SELECTED);
    strSub = m_FtpFile.GetItemText(i,0);

    if (i==-1)
    {
        AfxMessageBox("没有选择目录!",MB_OK | MB_ICONQUESTION);
    }
    else
    {   //判断是不是目录
        if ("<DIR>"!=m_FtpFile.GetItemText(i,2))
        {
            AfxMessageBox("不是子目录!",MB_OK | MB_ICONSTOP);
        }
        else
        {
            //设置当前目录
            m_pConnection->SetCurrentDirectory(strCurrentDirectory+strSub);
            //对当前目录进行查询
            ListContent("*");
        }
    }
}


//返回上一级目录
void CFtpDlg::OnLastdirectory()
{

    static CString  strCurrentDirectory;

    m_pConnection->GetCurrentDirectory(strCurrentDirectory);

    if (strCurrentDirectory == "/")
    {
        AfxMessageBox("已经是根目录了!",MB_OK | MB_ICONSTOP);
    }
    else
    {
        GetLastDiretory(strCurrentDirectory);
        //设置当前目录
        m_pConnection->SetCurrentDirectory(strCurrentDirectory);
        //对当前目录进行查询
        ListContent("*");
    }
}
//一工具函数,用于得到上一级目录的字符串表示
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



//当双击的时候,调用下一级目录代码,对文件不起作用
void CFtpDlg::OnDblclkListFile(NMHDR* pNMHDR, LRESULT* pResult)
{
    // TODO: Add your control notification handler code here
    OnNextdirectory();
    *pResult = 0;
}
//退出对话框响应函数
void CFtpDlg::OnExit()
{
    // TODO: Add your control notification handler code here
    m_pConnection = NULL;
    m_pFileFind = NULL;
    DestroyWindow();
}
