
// TestDlg.h : ͷ�ļ�
//

#pragma once
#include "afxcmn.h"



// CTestDlg �Ի���
class CTestDlg : public CDialogEx
{
// ����
public:


    CTestDlg(CWnd* pParent = NULL);	// ��׼���캯��

// �Ի�������
    enum { IDD = IDD_TEST_DIALOG };

protected:
    virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV ֧��


// ʵ��
protected:
    HICON m_hIcon;

    // ���ɵ���Ϣӳ�亯��
    virtual BOOL OnInitDialog();
    afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
    afx_msg void OnPaint();
    afx_msg HCURSOR OnQueryDragIcon();
    DECLARE_MESSAGE_MAP()
public:
    CIPAddressCtrl m_ip;
    int m_nServPort;
    afx_msg void OnBnClickedButton1();
    afx_msg void OnDestroy();
};
