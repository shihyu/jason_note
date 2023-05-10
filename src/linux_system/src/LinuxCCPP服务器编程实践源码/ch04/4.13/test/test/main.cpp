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
    service.sin_port = htons(8000);
    if (bind(s, (SOCKADDR*)&service, sizeof(service)) == -1) //���׽���
    {
        printf("bind failed:%d\n",errno);
        getchar();
        return -1;
    }
    int optVal;
    int optLen = sizeof(optVal);
    //��ȡѡ��SO_ACCEPTCONN��ֵ
    if (getsockopt(s, SOL_SOCKET, SO_ACCEPTCONN, (char*)&optVal, (socklen_t*)&optLen) == -1)
        printf("getsockopt failed:%d",errno);
    else printf("Before listening, The value of SO_ACCEPTCONN:%d, The socket is not listening\n", optVal);

    // ��ʼ����
    if (listen(s, 100) == -1)
    {
        printf("listen failed:%d\n", errno);
        getchar();
        return -1;
    }
    //��ȡѡ��SO_ACCEPTCONN��ֵ
    if (getsockopt(s, SOL_SOCKET, SO_ACCEPTCONN, (char*)&optVal, (socklen_t*)&optLen) == -1)
    {
        printf("getsockopt failed:%d", errno);
        getchar();
        return -1;
    }
    else printf("After listening,The value of SO_ACCEPTCONN:%d, The socket is listening\n", optVal);
    getchar();
    return 0;
}
