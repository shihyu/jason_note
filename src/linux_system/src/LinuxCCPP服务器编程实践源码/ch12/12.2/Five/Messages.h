//zww
// Messages.h
// 功能：定义消息结构及各种消息

#ifndef _MSGSTRUCT_
#define _MSGSTRUCT_

typedef struct _tagMsgStruct {
    // 消息ID
    UINT uMsg;
    // 落子信息
    int x;
    int y;
    int color;
    // 消息内容
    TCHAR szMsg[128];
} MSGSTRUCT;

#endif // _MSGSTRUCT_


// 落子消息
#define MSG_PUTSTEP     0x00000001
// 悔棋消息
#define MSG_BACK        0x00000002
// 同意悔棋消息
#define MSG_AGREEBACK   0x00000003
// 拒绝悔棋消息
#define MSG_REFUSEBACK  0x00000004
// 和棋消息
#define MSG_DRAW        0x00000005
// 同意和棋消息
#define MSG_AGREEDRAW   0x00000006
// 拒绝和棋消息
#define MSG_REFUSEDRAW  0x00000007
// 认输消息
#define MSG_GIVEUP      0x00000008
// 聊天消息
#define MSG_CHAT        0x00000009
// 对方信息消息
#define MSG_INFORMATION 0x0000000a
// 再次开局消息
#define MSG_PLAYAGAIN   0x0000000b
// 同意再次开局消息
#define MSG_AGREEAGAIN  0x0000000c