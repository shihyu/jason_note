typedef struct link {

    int fd;//代表套接字句柄

    char usrName[256]; //在线用户名

    char creatorIP[256]; //该用户创建棋盘所在客户机的ip

    int isFree,isCreator;//是否空闲没对手；是否是创建棋盘者

    struct link * next;//代表指针域，指向直接后继元素

} MYLINK;

