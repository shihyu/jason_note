#include <cstdio>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

int main()
{
    int serv_len,err;
    char on = 1;
    int sockSrv = socket(AF_INET, SOCK_STREAM, 0); //����һ���׽��֣����ڼ����ͻ��˵�����

    //�����ַ����������
    setsockopt(sockSrv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    struct sockaddr_in serv,addrSrv;
    memset(&addrSrv, 0, sizeof(struct sockaddr_in));
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118");
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000);  //ʹ�ö˿�8000

    if(-1==bind(sockSrv, (struct sockaddr *)&addrSrv, sizeof(struct sockaddr))) //��
    {
        printf("bind fail:%d!\r\n", errno);
        return -1;
    }
    //��ȡ�����׽��ֵ�ַ
    serv_len = sizeof(struct sockaddr_in);
    getsockname(sockSrv, (struct sockaddr *)&serv, (socklen_t*)&serv_len);
    //��ӡ�׽��ֵ�ַ���ip�Ͷ˿�ֵ���Ա��ÿͻ���֪��
    printf("server has started,ip=%s,port=%d\n", inet_ntoa(serv.sin_addr), ntohs(serv.sin_port));

    listen(sockSrv, 5); //����

    sockaddr_in addrClient;
    int len = sizeof(sockaddr_in);

    while (1)
    {
        printf("--------wait for client-----------\n");
        //���������������ȡ��������ǰ��һ���ͻ��������������Ϊ�վ;�����
        int sockConn = accept(sockSrv, (struct sockaddr *)&addrClient, (socklen_t*)&len);
        char sendBuf[100];
        sprintf(sendBuf, "Welcome client(%s) to Server!", inet_ntoa(addrClient.sin_addr));//����ַ���
        send(sockConn, sendBuf, strlen(sendBuf) + 1, 0); //�����ַ������ͻ���
        char recvBuf[100];
        recv(sockConn, recvBuf, 100, 0); //���տͻ�����Ϣ
        printf("Receive client's msg:%s\n", recvBuf); //��ӡ�յ��Ŀͻ�����Ϣ
        close(sockConn); //�رպͿͻ���ͨ�ŵ��׽���
        puts("continue to listen?(y/n)");
        char ch[2];
        scanf("%s", ch, 2); //������̨�����ַ��������س���
        if (ch[0] != 'y') //�������y���˳�ѭ��
            break;
    }
    close(sockSrv); //�رռ����׽���
    return 0;
}
