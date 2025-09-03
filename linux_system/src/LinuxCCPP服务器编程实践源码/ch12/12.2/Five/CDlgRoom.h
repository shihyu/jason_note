#pragma once


// CDlgRoom 对话框

class CDlgRoom : public CDialogEx
{
    DECLARE_DYNAMIC(CDlgRoom)

public:
    CDlgRoom(CWnd* pParent = nullptr);   // 标准构造函数
    virtual ~CDlgRoom();

// 对话框数据
#ifdef AFX_DESIGN_TIME
    enum { IDD = IDD_ROOM };
#endif

protected:
    virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

    DECLARE_MESSAGE_MAP()
public:
    void setOK();
    CListBox m_lst;
    afx_msg void OnBnClickedButtonCreate();
    afx_msg void OnBnClickedButtonAdd();
    virtual BOOL OnInitDialog();
};
