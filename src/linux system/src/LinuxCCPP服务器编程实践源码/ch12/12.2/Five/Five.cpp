//zww
// Five.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "Five.h"
#include "FiveDlg.h"
#include "CDlgLogin.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CFiveApp

BEGIN_MESSAGE_MAP(CFiveApp, CWinApp)
    //{{AFX_MSG_MAP(CFiveApp)
    // NOTE - the ClassWizard will add and remove mapping macros here.
    //    DO NOT EDIT what you see in these blocks of generated code!
    //}}AFX_MSG
    ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CFiveApp construction

CFiveApp::CFiveApp()
{
    // TODO: add construction code here,
    // Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CFiveApp object

CFiveApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CFiveApp initialization

BOOL CFiveApp::InitInstance()
{
    if (!AfxSocketInit())
    {
        AfxMessageBox(IDP_SOCKETS_INIT_FAILED);
        return FALSE;
    }

    // Standard initialization
    // If you are not using these features and wish to reduce the size
    //  of your final executable, you should remove from the following
    //  the specific initialization routines you do not need.

#ifdef _AFXDLL
    Enable3dControls();			// Call this when using MFC in a shared DLL
#else
    Enable3dControlsStatic();	// Call this when linking to MFC statically
#endif

    WSADATA wsd;
    AfxSocketInit(&wsd);
    m_clinetsock.Create();  //别忘记了

    //保存下本机IP,以后创建棋盘时候，要发布到大厅里。
    hostent *host;
    CHAR szHost[100];
    gethostname(szHost, 100);
    host = gethostbyname(szHost);
    for (int i = 0; host != NULL && host->h_addr_list[i] != NULL; i++)
    {
        strcpy(m_szMyIPAsCreator, inet_ntoa(*((in_addr *)host->h_addr_list[i])));
        //	AfxMessageBox(m_szIP);
        break;
    }




    CDlgLogin dlgLogin;
    if (IDOK != dlgLogin.DoModal())
        return FALSE;


    // 获得配置文件位置
    ::GetModuleFileName( NULL, m_szIni, MAX_PATH );
    lstrcpy( &m_szIni[lstrlen( m_szIni ) - 3], _T("ini") );
    // 读取战绩统计,以后扩展
    m_nWin = ::GetPrivateProfileInt( _T("Stats"), _T("Win"), 0, m_szIni );
    m_nDraw = ::GetPrivateProfileInt( _T("Stats"), _T("Draw"), 0, m_szIni );
    m_nLost = ::GetPrivateProfileInt( _T("Stats"), _T("Lost"), 0, m_szIni );
    // 注册棋盘窗口类
    WNDCLASS wc;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = 0;
    wc.hbrBackground = (HBRUSH)GetStockObject( WHITE_BRUSH );
    wc.hCursor = LoadCursor( IDC_ARROW );
    wc.hIcon = NULL;
    wc.hInstance = AfxGetInstanceHandle();
    wc.lpfnWndProc = ::DefWindowProc;
    wc.lpszClassName = _T("ChessTable");
    wc.lpszMenuName = NULL;
    wc.style = 0;
    AfxRegisterClass( &wc );
    CFiveDlg dlg;
    m_pMainWnd = &dlg;
    int nResponse = dlg.DoModal();
    if (nResponse == IDOK)
    {
        // TODO: Place code here to handle when the dialog is
        //  dismissed with OK
    }
    else if (nResponse == IDCANCEL)
    {
        // TODO: Place code here to handle when the dialog is
        //  dismissed with Cancel
    }

    // Since the dialog has been closed, return FALSE so that we exit the
    //  application, rather than start the application's message pump.
    return FALSE;
}
