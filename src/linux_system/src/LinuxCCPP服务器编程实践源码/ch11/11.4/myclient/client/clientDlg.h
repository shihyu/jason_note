
// clientDlg.h : ͷ�ļ�
//

#pragma once
#include "afxcmn.h"


// CclientDlg �Ի���
class CclientDlg : public CDialogEx
{
// ����
public:



    CclientDlg(CWnd* pParent = NULL);	// ��׼���캯��

// �Ի�������
    enum { IDD = IDD_CLIENT_DIALOG };

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
    afx_msg void OnBnClickedButton1();

    CIPAddressCtrl m_ip;
    int m_nServPort;
    afx_msg void OnBnClickedButtonReg();
    CEdit m_port;
    CEdit m_nick;
    CString m_strName;
};
