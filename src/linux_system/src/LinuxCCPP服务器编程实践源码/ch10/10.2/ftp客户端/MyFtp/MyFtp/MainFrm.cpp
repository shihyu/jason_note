//created by zww
// MainFrm.cpp : implementation of the CMainFrame class
//

#include "stdafx.h"
#include "MyFtp.h"

#include "MainFrm.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMainFrame

IMPLEMENT_DYNCREATE(CMainFrame, CFrameWnd)

BEGIN_MESSAGE_MAP(CMainFrame, CFrameWnd)
//{{AFX_MSG_MAP(CMainFrame)
    ON_WM_CREATE()
    ON_WM_TIMER()
    ON_COMMAND(IDM_EXIT, OnExit)
    ON_WM_CLOSE()
//}}AFX_MSG_MAP
END_MESSAGE_MAP()

static UINT indicators[] =
{
    ID_SEPARATOR,           // status line indicator
    IDS_TIMER,
    //	IDS_PROGRESS,
    //	ID_INDICATOR_CAPS,
    //	ID_INDICATOR_NUM,
    //	ID_INDICATOR_SCRL,
};

/////////////////////////////////////////////////////////////////////////////
// CMainFrame construction/destruction

CMainFrame::CMainFrame()
{
    // TODO: add member initialization code here
    //	m_bAutoMenuEnable = FALSE;
}

CMainFrame::~CMainFrame()
{
}

int CMainFrame::OnCreate(LPCREATESTRUCT lpCreateStruct)
{
    if (CFrameWnd::OnCreate(lpCreateStruct) == -1)
        return -1;

    if (!m_wndStatusBar.Create(this) ||
            !m_wndStatusBar.SetIndicators(indicators,
                                          sizeof(indicators)/sizeof(UINT)))
    {
        TRACE0("Failed to create status bar\n");
        return -1;      // fail to create
    }

    // TODO: Delete these three lines if you don't want the toolbar to
    //  be dockable

    //WS_OVERLAPPED������ָ�б������б߿�Ĵ���
    MoveWindow(CRect(0, 0, 405 + 150, 205 + 120));
    CenterWindow();
    //	SetWindowLong(m_hWnd,GWL_STYLE,GetWindowLong(m_hWnd,GWL_STYLE)&~WS_OVERLAPPED);
    SetTimer(1,1000,NULL);  //һ�뷢��WM_TIMER��Ϣ
    return 0;
}

BOOL CMainFrame::PreCreateWindow(CREATESTRUCT& cs)
{
    if( !CFrameWnd::PreCreateWindow(cs) )
        return FALSE;
    // TODO: Modify the Window class or styles here by modifying
    //  the CREATESTRUCT cs
    //���ô��ڵĴ�С
    cs.cx=450;
    cs.cy=550;

    return TRUE;
}

/////////////////////////////////////////////////////////////////////////////
// CMainFrame diagnostics

#ifdef _DEBUG
void CMainFrame::AssertValid() const
{
    CFrameWnd::AssertValid();
}

void CMainFrame::Dump(CDumpContext& dc) const
{
    CFrameWnd::Dump(dc);
}

#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CMainFrame message handlers


void CMainFrame::OnTimer(UINT nIDEvent)
{
    // TODO: Add your message handler code here and/or call default

    //������״̬����ʾ��ǰʱ��
    CTime t=CTime::GetCurrentTime();
    CString str=t.Format("%H:%M:%S");

    CClientDC dc(this);
    CSize sz=dc.GetTextExtent(str);

    m_wndStatusBar.SetPaneInfo(1,IDS_TIMER,SBPS_NORMAL,sz.cx);
    m_wndStatusBar.SetPaneText(1,str);

    CFrameWnd::OnTimer(nIDEvent);
}

void CMainFrame::OnExit()
{
    // TODO: Add your command handler code here
    //�˳��������Ӧ����
    if(IDYES==MessageBox("ȷ��Ҫ�˳��ͻ�����?","����",MB_YESNO|MB_ICONWARNING))
        CFrameWnd::OnClose();
}

void CMainFrame::OnClose()
{
    // TODO: Add your message handler code here and/or call default
    //WM_CLOSE����Ӧ����
    OnExit();
}
