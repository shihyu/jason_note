//zww
// Messages.h
// ���ܣ�������Ϣ�ṹ��������Ϣ

#ifndef _MSGSTRUCT_
#define _MSGSTRUCT_

typedef struct _tagMsgStruct {
    // ��ϢID
    UINT uMsg;
    // ������Ϣ
    int x;
    int y;
    int color;
    // ��Ϣ����
    TCHAR szMsg[128];
} MSGSTRUCT;

#endif // _MSGSTRUCT_


// ������Ϣ
#define MSG_PUTSTEP     0x00000001
// ������Ϣ
#define MSG_BACK        0x00000002
// ͬ�������Ϣ
#define MSG_AGREEBACK   0x00000003
// �ܾ�������Ϣ
#define MSG_REFUSEBACK  0x00000004
// ������Ϣ
#define MSG_DRAW        0x00000005
// ͬ�������Ϣ
#define MSG_AGREEDRAW   0x00000006
// �ܾ�������Ϣ
#define MSG_REFUSEDRAW  0x00000007
// ������Ϣ
#define MSG_GIVEUP      0x00000008
// ������Ϣ
#define MSG_CHAT        0x00000009
// �Է���Ϣ��Ϣ
#define MSG_INFORMATION 0x0000000a
// �ٴο�����Ϣ
#define MSG_PLAYAGAIN   0x0000000b
// ͬ���ٴο�����Ϣ
#define MSG_AGREEAGAIN  0x0000000c