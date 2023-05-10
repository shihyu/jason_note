#include <cstdio>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main()
{
    int err;
    int  sockClient = socket(AF_INET, SOCK_STREAM, 0);//�½�һ���׽���
    char msg[] = "hi,server"; //Ҫ���͸��������˵���Ϣ
    sockaddr_in addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //��������IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //�������ļ����˿�
    err = connect(sockClient, (struct sockaddr *)&addrSrv, sizeof(struct sockaddr)); //�������������������
    if (-1 == err) //�ж������Ƿ�ɹ�
    {
        printf("Failed to connect to the server.Please check whether the server is started\n");
        return 0;
    }
    char recvBuf[100];
    recv(sockClient, recvBuf, 100, 0); //�������Է���������Ϣ
    printf("receive server's msg:%s\n", recvBuf); //��ӡ�յ�����Ϣ
    send(sockClient, msg, strlen(msg) + 1, 0); //�������������Ϣ
    close(sockClient); //�ر��׽���
    getchar();

    return 0;
}
