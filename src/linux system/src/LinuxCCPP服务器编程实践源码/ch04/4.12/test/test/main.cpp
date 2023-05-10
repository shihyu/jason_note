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

int main()
{
    int err;
    int s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); //�������׽���
    if (s == -1) {
        printf("Error at socket()\n");
        return -1;
    }
    int su = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP); //�������ݱ��׽���
    if (s == -1) {
        printf("Error at socket()\n");
        return -1;
    }

    int optVal;
    int optLen = sizeof(optVal);
    //��ȡ�׽���s������
    if (getsockopt(s, SOL_SOCKET, SO_TYPE, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
    {
        if (SOCK_STREAM == optVal) // SOCK_STREAM�궨��ֵΪ1
            printf("The current socket is a stream socket.\n"); //��ǰ�׽��������׽���
        else if (SOCK_DGRAM == optVal) // SOCK_ DGRAM�궨��ֵΪ2
            printf("The current socket is a datagram socket.\n");//��ǰ�׽��������ݱ��׽���
    }
    //��ȡ�׽���su������
    if (getsockopt(su, SOL_SOCKET, SO_TYPE, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
    {
        if (SOCK_STREAM == optVal)  // SOCK_STREAM�궨��ֵΪ1
            printf("The current socket is a stream socket.\n");
        else if (SOCK_DGRAM == optVal) // SOCK_ DGRAM�궨��ֵΪ2
            printf("The current socket is a datagram socket.\n");
    }
    getchar();
    return 0;
}
