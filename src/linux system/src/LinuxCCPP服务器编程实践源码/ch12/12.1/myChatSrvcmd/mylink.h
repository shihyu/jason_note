typedef struct link {

    int fd;//�����׽��־��

    char usrName[256]; //�����û���

    char creatorIP[256]; //���û������������ڿͻ�����ip

    int isFree,isCreator;//�Ƿ����û���֣��Ƿ��Ǵ���������

    struct link * next;//����ָ����ָ��ֱ�Ӻ��Ԫ��

} MYLINK;

