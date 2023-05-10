#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
char rbuf[50];
int main()
{
    int sockfd, size, ret;
    char on = 1;
    struct sockaddr_in saddr;
    struct sockaddr_in raddr;

    //���õ�ַ��Ϣ��ip��Ϣ
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(8888);
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);

    //����udp ���׽���
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        puts("socket failed");
        return -1;
    }

    //���ö˿ڸ���
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //�󶨵�ַ��Ϣ��ip��Ϣ
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        puts("sbind failed");
        return -1;
    }

    int  val = sizeof(struct sockaddr);
    //ѭ�����տͻ��˷�������Ϣ
    while (1)
    {
        puts("waiting data");
        ret = recvfrom(sockfd, rbuf, 50, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
        if (ret < 0)
        {
            perror("recvfrom failed");
        }

        printf("recv data :%s\n", rbuf);
        memset(rbuf, 0, 50);
    }
    //�ر�udp�׽��֣����ﲻ�ɴ�ġ�
    close(sockfd);
    getchar();
    return 0;
}
