//zww
#ifndef CLASS_TABLE
#define CLASS_TABLE

#include "Game.h"
#include "FiveSocket.h"

class CTable : public CWnd
{
    CImageList m_iml; // ����ͼ��
    int m_color; // �����ɫ
    BOOL m_bWait; // �ȴ���־
    void Draw(int x, int y, int color);
    CGame *m_pGame; // ��Ϸģʽָ��
public:
    void PlayAgain();
    void SetMenuState( BOOL bEnable );
    void GiveUp();
    void RestoreWait();
    BOOL m_bOldWait; // ��ǰ�ĵȴ���־
    void Chat( LPCTSTR lpszMsg );
    // �Ƿ��������磨�ͻ���ʹ�ã�
    BOOL m_bConnected;
    // �ҷ�����
    CString m_strMe;
    // �Է�����
    CString m_strAgainst;
    // �������׽���
    CFiveSocket m_conn;
    CFiveSocket m_sock;
    int m_data[15][15]; // ��������
    CTable();
    ~CTable();
    void Clear( BOOL bWait );
    void SetColor(int color);
    int GetColor() const;
    BOOL SetWait( BOOL bWait );
    void SetData( int x, int y, int color );
    BOOL Win(int color) const;
    void DrawGame();
    void SetGameMode( int nGameMode );
    void Back();
    void Over();
    void Accept( int nGameMode );
    void Connect( int nGameMode );
    void Receive();
protected:
    afx_msg void OnPaint();
    afx_msg void OnLButtonUp( UINT nFlags, CPoint point );
    DECLARE_MESSAGE_MAP()
};

#endif // CLASS_TABLE