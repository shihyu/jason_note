#include <cstdio>
#include <assert.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define BUF_LEN 300
typedef struct sockaddr_in SOCKADDR_IN;
typedef struct sockaddr SOCKADDR;
int main()
{

    int err;
    long argp;
    char szMsg[] = "Hello, server, I have received your message.";

    int sockClient = socket(AF_INET, SOCK_STREAM, 0);//�½�һ���׽���

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //��������IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //�������ļ����˿�
    err = connect(sockClient, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //�������������������
    if (-1 == err) //�ж������Ƿ�ɹ�
    {
        printf("Failed to connect to the server. Please check whether the server is started\n");
        getchar();
        return 0;
    }
    char recvBuf[BUF_LEN];
    int i, cn = 1, iRes;
    do
    {
        iRes = recv(sockClient, recvBuf, BUF_LEN, 0); //�������Է���������Ϣ
        if (iRes > 0)
        {
            printf("\nRecv %d bytes:", iRes);
            for (i = 0; i < iRes; i++)
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//�Է��ر�����
            puts("The server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return 1;
        }

    } while (iRes > 0);
    //��ʼ��ͻ��˷�������
    char sendBuf[100];
    for (i = 0; i < 10; i++)
    {
        sprintf(sendBuf, "N0.%d I'm the client,1+1=2\n", i + 1);//����ַ���
        send(sockClient, sendBuf, strlen(sendBuf) + 1, 0); //�����ַ������ͻ���
        memset(sendBuf, 0, sizeof(sendBuf));
    }
    puts("Sending data to the server is completed.");
    close(sockClient); //�ر��׽���
    getchar();
    return 0;
}
