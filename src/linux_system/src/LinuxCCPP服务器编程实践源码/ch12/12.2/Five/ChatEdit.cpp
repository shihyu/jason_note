//Download by http://www.NewXing.com
// ChatEdit.cpp : implementation file
//

#include "stdafx.h"
#include "five.h"
#include "ChatEdit.h"
#include "Table.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CChatEdit

CChatEdit::CChatEdit()
{
}

CChatEdit::~CChatEdit()
{
}


BEGIN_MESSAGE_MAP(CChatEdit, CEdit)
    //{{AFX_MSG_MAP(CChatEdit)
    ON_WM_KEYDOWN()
    //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CChatEdit message handlers

void CChatEdit::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)
{
    // TODO: Add your message handler code here and/or call default
    if ( '6' == nChar )
    {
        CTable *pTable = (CTable *)( AfxGetMainWnd()->GetDlgItem( IDC_TABLE ) );
        // 发送聊天信息
        TCHAR str[128];
        GetWindowText( str, 128 );
        pTable->Chat( str );
        // 写入聊天记录
        CEdit *pEdit = (CEdit *)( AfxGetMainWnd()->GetDlgItem( IDC_EDT_CHAT ) );
        CString strAdd;
        strAdd.Format( _T("你 说：%s\r\n"), str );
        pEdit->SetSel( -1, -1, TRUE );
        pEdit->ReplaceSel( str );
        SetWindowText( _T("") );
    }
    else
    {
        CEdit::OnKeyDown(nChar, nRepCnt, nFlags);
    }
}
