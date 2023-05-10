
#ifndef CLASS_GAME
#define CLASS_GAME

#ifndef _LIST_
#include <list>
using std::list;
#endif

#include "Messages.h"

class CTable;

typedef struct _tagStep {
    int x;
    int y;
    int color;
} STEP;

// ��Ϸ����
class CGame
{
protected:
    CTable *m_pTable;
public:
    // ���Ӳ���
    list< STEP > m_StepList;
public:
    // ���캯��
    CGame( CTable *pTable ) : m_pTable( pTable ) {}
    // ��������
    virtual ~CGame();
    // ��ʼ����������ͬ����Ϸ��ʽ��ʼ��Ҳ��һ��
    virtual void Init() = 0;
    // ����ʤ����������CTwoGame��Ҫ��д�˺�������ƺ���
    virtual void Win( const STEP& stepSend );
    // ���ͼ�������
    virtual void SendStep( const STEP& stepSend ) = 0;
    // ���նԷ���Ϣ
    virtual void ReceiveMsg( MSGSTRUCT *pMsg ) = 0;
    // ���ͻ�������
    virtual void Back() = 0;
};

// һ����Ϸ������
class COneGame : public CGame
{
    bool m_Computer[15][15][572]; // ���Ի�ʤ���
    bool m_Player[15][15][572]; // ��һ�ʤ���
    int m_Win[2][572]; // ������ʤ����������������
    bool m_bStart; // ��Ϸ�Ƿ�ոտ�ʼ
    STEP m_step; // �������ӽ��
    // ����������Ա������֮��
    bool m_bOldPlayer[572];
    bool m_bOldComputer[572];
    int m_nOldWin[2][572];
public:
    COneGame( CTable *pTable ) : CGame( pTable ) {}
    virtual ~COneGame();
    virtual void Init();
    virtual void SendStep( const STEP& stepSend );
    virtual void ReceiveMsg( MSGSTRUCT *pMsg );
    virtual void Back();
private:
    // ��������һ���Ӻ�ķ���
    int GiveScore( const STEP& stepPut );
    void GetTable( int tempTable[][15], int nowTable[][15] );
    bool SearchBlank( int &i, int &j, int nowTable[][15] );
};

// ������Ϸ������
class CTwoGame : public CGame
{
public:
    CTwoGame( CTable *pTable ) : CGame( pTable ) {}
    virtual ~CTwoGame();
    virtual void Init();
    virtual void Win( const STEP& stepSend );
    virtual void SendStep( const STEP& stepSend );
    virtual void ReceiveMsg( MSGSTRUCT *pMsg );
    virtual void Back();
};

#endif // CLASS_GAME