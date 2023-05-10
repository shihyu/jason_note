
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

// 游戏基类
class CGame
{
protected:
    CTable *m_pTable;
public:
    // 落子步骤
    list< STEP > m_StepList;
public:
    // 构造函数
    CGame( CTable *pTable ) : m_pTable( pTable ) {}
    // 析构函数
    virtual ~CGame();
    // 初始化工作，不同的游戏方式初始化也不一样
    virtual void Init() = 0;
    // 处理胜利后的情况，CTwoGame需要改写此函数完成善后工作
    virtual void Win( const STEP& stepSend );
    // 发送己方落子
    virtual void SendStep( const STEP& stepSend ) = 0;
    // 接收对方消息
    virtual void ReceiveMsg( MSGSTRUCT *pMsg ) = 0;
    // 发送悔棋请求
    virtual void Back() = 0;
};

// 一人游戏派生类
class COneGame : public CGame
{
    bool m_Computer[15][15][572]; // 电脑获胜组合
    bool m_Player[15][15][572]; // 玩家获胜组合
    int m_Win[2][572]; // 各个获胜组合中填入的棋子数
    bool m_bStart; // 游戏是否刚刚开始
    STEP m_step; // 保存落子结果
    // 以下三个成员做悔棋之用
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
    // 给出下了一个子后的分数
    int GiveScore( const STEP& stepPut );
    void GetTable( int tempTable[][15], int nowTable[][15] );
    bool SearchBlank( int &i, int &j, int nowTable[][15] );
};

// 二人游戏派生类
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