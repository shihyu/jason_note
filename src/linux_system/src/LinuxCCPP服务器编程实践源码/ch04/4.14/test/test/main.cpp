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
#include <sys/ioctl.h>
typedef struct sockaddr SOCKADDR;
int main()
{
    int err;
    sockaddr_in service;
    char ip[] = "192.168.0.118";//����ip
    char on = 1;

    int s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); //����һ�����׽���
    if (s == -1) {
        printf("Error at socket()\n");
        getchar();
        return -1;
    }
    //�����ַ����������
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    service.sin_family = AF_INET;
    service.sin_addr.s_addr = inet_addr(ip);
    service.sin_port = htons(9900);
    if (bind(s, (SOCKADDR*)&service, sizeof(service)) == -1) //���׽���
    {
        printf("bind failed\n");
        getchar();
        return -1;
    }


    int  optVal = 1;//һ��Ҫ��ʼ��
    int optLen = sizeof(int);

    //��ȡѡ��SO_KEEPALIVE��ֵ
    if (getsockopt(s, SOL_SOCKET, SO_KEEPALIVE, (char*)&optVal, (socklen_t *)&optLen) == -1)
    {
        printf("getsockopt failed:%d", errno);
        getchar();
        return -1;
    }
    else printf("After listening,the value of SO_ACCEPTCONN:%d\n", optVal);

    optVal = 1;
    if (setsockopt(s, SOL_SOCKET, SO_KEEPALIVE, (char*)&optVal, optLen) != -1)
    {
        printf("Successful activation of keep alive mechanism.\n");//���ñ�����Ƴɹ�
    }
    if (getsockopt(s, SOL_SOCKET, SO_KEEPALIVE, (char*)&optVal, (socklen_t *)&optLen) == -1)
    {
        printf("getsockopt failed:%d", errno);
        getchar();
        return -1;
    }
    else printf("After setting,the value of SO_KEEPALIVE:%d\n", optVal);
    getchar();
    return 0;
}
