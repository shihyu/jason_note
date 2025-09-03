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

#define BUF_LEN 250
typedef struct sockaddr_in SOCKADDR_IN;
typedef struct sockaddr SOCKADDR;
int main()
{
    int err;
    u_long argp;
    char szMsg[] = "Hello, server, I have received your message.";
    int sockClient = socket(AF_INET, SOCK_STREAM, 0);//�½�һ���׽���

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //��������IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //�������ļ����˿�
    err = connect(sockClient, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //�������������������
    if (-1 == err) //�ж������Ƿ�ɹ�
    {
        printf("Failed to connect to the server:%d\n",errno);
        getchar();
        return 0;
    }
    char recvBuf[BUF_LEN];// BUF_LEN��250
    int i, cn = 1, iRes;
    int leftlen = 50 * 111;//���5550��ͨ��˫��Լ�õ�
    while (leftlen > BUF_LEN)
    {
        //�������Է���������Ϣ��ÿ�����ֻ�ܽ���BUF_LEN�����ݣ�������ն���δ֪
        iRes = recv(sockClient, recvBuf, BUF_LEN, 0);
        if (iRes > 0)
        {
            printf("\nNo.%d:Recv %d bytes:", cn++, iRes);
            for (i = 0; i < iRes; i++) //��ӡ���ν��յ�������
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//�Է��ر�����
            puts("\nThe server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return -1;
        }
        leftlen = leftlen - iRes;
    }
    if (leftlen > 0)
    {
        iRes = recv(sockClient, recvBuf, leftlen, 0);
        if (iRes > 0)
        {
            printf("\nNo.%d:Recv %d bytes:", cn++, iRes);
            for (i = 0; i < iRes; i++) //��ӡ���ν��յ�������
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//�Է��ر�����
            puts("\nThe server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return -1;
        }
        leftlen = leftlen - iRes;
    }




    //��ʼ�����˷�������
    char sendBuf[100];
    sprintf(sendBuf, "Hi,Server,I've finished receiving the data.");//����ַ���
    send(sockClient, sendBuf, strlen(sendBuf) + 1, 0); //�����ַ������ͻ���
    memset(sendBuf, 0, sizeof(sendBuf));

    puts("Sending data to the server is completed");
    close(sockClient); //�ر��׽���
    getchar();
    return 0;
}
