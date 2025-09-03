//created by zww
// MyFtpView.cpp : implementation of the CMyFtpView class
//

#include "stdafx.h"
#include "MyFtp.h"

#include "MyFtpDoc.h"
#include "MyFtpView.h"
#include "MainFrm.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView

IMPLEMENT_DYNCREATE(CMyFtpView, CView)

BEGIN_MESSAGE_MAP(CMyFtpView, CView)
//{{AFX_MSG_MAP(CMyFtpView)
    ON_WM_ERASEBKGND()
    ON_COMMAND(IDM_CONNECT, OnConnect)
    ON_WM_TIMER()
//}}AFX_MSG_MAP
// Standard printing commands
    ON_COMMAND(ID_FILE_PRINT, CView::OnFilePrint)
    ON_COMMAND(ID_FILE_PRINT_DIRECT, CView::OnFilePrint)
    ON_COMMAND(ID_FILE_PRINT_PREVIEW, CView::OnFilePrintPreview)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView construction/destruction

CMyFtpView::CMyFtpView()
{
    // TODO: add construction code here
    m_FtpWebSite = _T("");
    m_UserName = _T("");
    m_UserPwd = _T("");
    m_pSession = NULL;
    m_pConnection = NULL;
    m_pFileFind = NULL;
}

CMyFtpView::~CMyFtpView()
{
}

BOOL CMyFtpView::PreCreateWindow(CREATESTRUCT& cs)
{
    // TODO: Modify the Window class or styles here by modifying
    //  the CREATESTRUCT cs

    return CView::PreCreateWindow(cs);
}

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView drawing

void CMyFtpView::OnDraw(CDC* pDC)
{
    CMyFtpDoc* pDoc = GetDocument();
    ASSERT_VALID(pDoc);
    // TODO: add draw code for native data here
}

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView printing

BOOL CMyFtpView::OnPreparePrinting(CPrintInfo* pInfo)
{
    // default preparation
    return DoPreparePrinting(pInfo);
}

void CMyFtpView::OnBeginPrinting(CDC* /*pDC*/, CPrintInfo* /*pInfo*/)
{
    // TODO: add extra initialization before printing
}

void CMyFtpView::OnEndPrinting(CDC* /*pDC*/, CPrintInfo* /*pInfo*/)
{
    // TODO: add cleanup after printing
}

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView diagnostics

#ifdef _DEBUG
void CMyFtpView::AssertValid() const
{
    CView::AssertValid();
}

void CMyFtpView::Dump(CDumpContext& dc) const
{
    CView::Dump(dc);
}

CMyFtpDoc* CMyFtpView::GetDocument() // non-debug version is inline
{
    ASSERT(m_pDocument->IsKindOf(RUNTIME_CLASS(CMyFtpDoc)));
    return (CMyFtpDoc*)m_pDocument;
}
#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CMyFtpView message handlers


BOOL CMyFtpView::OnEraseBkgnd(CDC* pDC)    //用于添加背景图
{
    // TODO: Add your message handler code here and/or call default
    CBitmap bitmap;
    bitmap.LoadBitmap(IDB_BITMAP2);

    CDC dcCompatible;
    dcCompatible.CreateCompatibleDC(pDC);

    //创建与当前DC(pDC)兼容的DC,先用dcCompatible准备图像,再将数据复制到实际DC中
    dcCompatible.SelectObject(&bitmap);

    CRect rect;
    GetClientRect(&rect);//得到目的DC客户区大小,GetClientRect(&rect);
    //得到目的DC客户区大小,
    //pDC->BitBlt(0,0,rect.Width(),rect.Height(),&dcCompatible,0,0,SRCCOPY);//实现1:1的Copy

    BITMAP bmp;//结构体
    bitmap.GetBitmap(&bmp);
    pDC->StretchBlt(0,0,rect.Width(),rect.Height(),&dcCompatible,0,0,
                    bmp.bmWidth,bmp.bmHeight,SRCCOPY);
    return true;
}


void CMyFtpView::OnConnect()
{
    // TODO: Add your command handler code here
    //生成一个模态对话框
    if (IDOK==m_ConDlg.DoModal())
    {
        m_pConnection = NULL;
        m_pSession = NULL;

        m_FtpWebSite = m_ConDlg.m_FtpWebSite;
        m_UserName = m_ConDlg.m_UserName;
        m_UserPwd = m_ConDlg.m_UserPwd;

        m_pSession=new CInternetSession(AfxGetAppName(),
                                        1,
                                        PRE_CONFIG_INTERNET_ACCESS);
        try
        {
            //试图建立FTP连接
            SetTimer(1,1000,NULL);  //设置定时器,一秒发一次WM_TIMER
            CString  str="正在连接中....";
            ((CMainFrame*)GetParent())->SetMessageText(str);

            m_pConnection=m_pSession->GetFtpConnection(m_FtpWebSite,
                          m_UserName,m_UserPwd);
        }
        catch (CInternetException* e)
        {
            //错误处理
            e->Delete();
            m_pConnection=NULL;
        }
    }
}

void CMyFtpView::OnTimer(UINT nIDEvent)
{
    // TODO: Add your message handler code here and/or call default
    static int time_out=1;
    time_out++;
    if (m_pConnection == NULL)
    {
        CString  str="正在连接中....";
        ((CMainFrame*)GetParent())->SetMessageText(str);
        if (time_out>=60)
        {
            ((CMainFrame*)GetParent())->SetMessageText("连接超时!");
            KillTimer(1);
            MessageBox("连接超时!","超时",MB_OK);
        }
    }
    else
    {
        CString str="连接成功!";
        ((CMainFrame*)GetParent())->SetMessageText(str);

        KillTimer(1);
        //连接成功之后,不用定时器来监视连接情况
        //同时跳出操作对话框

        m_FtpDlg.m_pConnection = m_pConnection;
        //非模态对话框
        m_FtpDlg.Create(IDD_DIALOG2,this);
        m_FtpDlg.ShowWindow(SW_SHOW);
    }
    CView::OnTimer(nIDEvent);
}


void CMyFtpView::OnInitialUpdate()
{
    CView::OnInitialUpdate();

    // TODO: 在此添加专用代码和/或调用基类

}
