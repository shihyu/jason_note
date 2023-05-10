//zww
#if !defined(AFX_FIVESOCKET_H__A7C88E4D_BB5E_4598_BB32_3BD8C8020415__INCLUDED_)
#define AFX_FIVESOCKET_H__A7C88E4D_BB5E_4598_BB32_3BD8C8020415__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// FiveSocket.h : header file
//



/////////////////////////////////////////////////////////////////////////////
// CFiveSocket command target

class CFiveSocket : public CAsyncSocket
{
// Attributes
public:

// Operations
public:
    CFiveSocket();
    virtual ~CFiveSocket();

// Overrides
public:
    // ClassWizard generated virtual function overrides
    //{{AFX_VIRTUAL(CFiveSocket)
    //}}AFX_VIRTUAL

    // Generated message map functions
    //{{AFX_MSG(CFiveSocket)
    // NOTE - the ClassWizard will add and remove member functions here.
    //}}AFX_MSG

// Implementation
protected:
    virtual void OnAccept( int nErrorCode );
    virtual void OnConnect( int nErrorCode );
    virtual void OnReceive( int nErrorCode );
    virtual void OnClose( int nErrorCode );
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_FIVESOCKET_H__A7C88E4D_BB5E_4598_BB32_3BD8C8020415__INCLUDED_)
