#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
char wbuf[50];
int main()
{
    int sockfd, size, ret;
    char on = 1;
    struct sockaddr_in saddr;
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);

    //���ý��ն˵ĵ�ַ��Ϣ
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(9999); //ע������ǽ��ն˵Ķ˿�
    saddr.sin_addr.s_addr = inet_addr("192.168.0.153");//���ip���������ip

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);  //����udp ���׽���
    if (sockfd < 0)
    {
        perror("failed socket");
        return -1;
    }
    //���ö˿ڸ���
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    puts("please enter data:");
    scanf("%s", wbuf, sizeof(wbuf)); //����Ҫ���͵���Ϣ
    ret = sendto(sockfd, wbuf, sizeof(wbuf), 0, (struct sockaddr*)&saddr,
                 sizeof(struct sockaddr)); //������Ϣ�����ն�
    if (ret < 0) 	perror("sendto failed");
    close(sockfd);
    getchar();
    return 0;
}
