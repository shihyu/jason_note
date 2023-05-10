#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
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
    saddr.sin_port = htons(9999);
    saddr.sin_addr.s_addr = inet_addr("192.168.0.153");

    //����udp ���׽���
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket failed");
        return -1;
    }
    //���ö˿ڸ���
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //�ѽ��ն˵�ַ��Ϣ�󶨵��׽�����
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        perror("sbind failed");
        return -1;
    }
    int  val = sizeof(struct sockaddr);
    puts("waiting data");
    //�����ȴ����Ͷ˵���Ϣ
    ret = recvfrom(sockfd, rbuf, 50, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
    if (ret < 0)
        perror("recvfrom failed");
    printf("recv data :%s\n", rbuf); //��ӡ�յ�����Ϣ
    close(sockfd);//�ر�udp�׽���
    getchar();
    return 0;
}
