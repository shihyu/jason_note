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
    int err, i, iRes;
    char on = 1;
    int sockSrv = socket(AF_INET, SOCK_STREAM, 0); //����һ���׽��֣����ڼ����ͻ��˵�����
    assert(sockSrv >= 0);
    //�����ַ����������
    setsockopt(sockSrv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118");
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000);  //ʹ�ö˿�8000

    bind(sockSrv, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //��
    listen(sockSrv, 5); //����

    SOCKADDR_IN addrClient;
    int cn = 0, len = sizeof(SOCKADDR);

    while (1)
    {
        printf("--------wait for client-----------\n");
        //���������������ȡ��������ǰ��һ���ͻ��������������Ϊ�վ;�����
        int sockConn = accept(sockSrv, (SOCKADDR*)&addrClient, (socklen_t*)&len);
        char sendBuf[111] = "";
        printf("--------client comes-----------\n");
        for (cn = 0; cn < 50; cn++)
        {
            memset(sendBuf, 'a', 111);
            if (cn == 49)
                sendBuf[110] = 'b'; //�����һ���ַ�Ϊ'b',�������������һ��
            send(sockConn, sendBuf, 111, 0); //�����ַ������ͻ���
        }
        //���ͽ�������ʼ���տͻ��˷�������Ϣ
        char recvBuf[BUF_LEN];

        // �������տͻ������ݣ�ֱ���Է��ر�����
        do {

            iRes = recv(sockConn, recvBuf, BUF_LEN, 0);
            if (iRes > 0)
            {
                printf("\nRecv %d bytes:", iRes);
                for (i = 0; i < iRes; i++)
                    printf("%c", recvBuf[i]);
                printf("\n");
            }
            else if (iRes == 0)
                printf("The client closes the connection.\n");
            else
            {
                printf("recv failed with error: %d\n", errno);
                close(sockConn);
                return 1;
            }

        } while (iRes > 0);

        close(sockConn); //�رպͿͻ���ͨ�ŵ��׽���
        puts("Continue monitoring?(y/n)");
        char ch[2];
        scanf("%s", ch, 2); //������̨�����ַ��������س���
        if (ch[0] != 'y') //�������y���˳�ѭ��
            break;
    }
    close(sockSrv); //�رռ����׽���
    return 0;
}
