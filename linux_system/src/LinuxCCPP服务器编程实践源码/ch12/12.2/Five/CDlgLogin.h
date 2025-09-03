#pragma once


// CDlgLogin 对话框

class CDlgLogin : public CDialogEx
{
    DECLARE_DYNAMIC(CDlgLogin)

public:
    CDlgLogin(CWnd* pParent = nullptr);   // 标准构造函数
    virtual ~CDlgLogin();

// 对话框数据
#ifdef AFX_DESIGN_TIME
    enum { IDD = IDD_LOGIN };
#endif

protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

    DECLARE_MESSAGE_MAP()
public:
    void setOK();
    CIPAddressCtrl m_ip;
    int m_nServPort;
    CString m_strName;
    CEdit m_port;
    afx_msg void OnBnClickedButtonLogin();
    virtual BOOL OnInitDialog();
    CEdit m_nick;
    afx_msg void OnBnClickedReg();
};
