#include <cstdio>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc, char *argv[])
{
    unsigned short port = 8888;		// ���ض˿�
    char on = 1;
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);//1.����tcp�׽���
    if (sockfd < 0)
    {
        perror("socket");
        exit(-1);
    }
    //���ñ���������Ϣ
    struct sockaddr_in my_addr;
    bzero(&my_addr, sizeof(my_addr));	  // ���
    my_addr.sin_family = AF_INET;		  // IPv4
    my_addr.sin_port = htons(port);	  // �˿�
    my_addr.sin_addr.s_addr = htonl(INADDR_ANY); // ip
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));//���ö˿ڸ���
    int err_log = bind(sockfd, (struct sockaddr*)&my_addr, sizeof(my_addr));//2.��
    if (err_log != 0)
    {
        perror("binding");
        close(sockfd);
        getchar();
        exit(-1);
    }
    err_log = listen(sockfd, 10);//3.�������׽��ֱ䱻��
    if (err_log != 0)
    {
        perror("listen");
        close(sockfd);
        exit(-1);
    }
    while (1) //������ ѭ���ȴ��ͻ��˵�����
    {
        char cli_ip[INET_ADDRSTRLEN] = { 0 };
        struct sockaddr_in client_addr;
        socklen_t cliaddr_len = sizeof(client_addr);
        puts("Father process is waitting client...");
        // ȡ���ͻ�������ɵ�����
        int connfd = accept(sockfd, (struct sockaddr*)&client_addr, &cliaddr_len);
        if (connfd < 0)
        {
            perror("accept");
            close(sockfd);
            exit(-1);
        }
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            _exit(-1);
        }
        else if (0 == pid) { //�ӽ��� ���տͻ��˵���Ϣ�������ظ��ͻ���
            close(sockfd);   // �رռ����׽��֣�����׽����ǴӸ����̼̳й���
            char recv_buf[1024] = { 0 };
            int recv_len = 0;
            // ��ӡ�ͻ��˵� ip �Ͷ˿�
            memset(cli_ip, 0, sizeof(cli_ip)); // ���
            inet_ntop(AF_INET, &client_addr.sin_addr, cli_ip, INET_ADDRSTRLEN);
            printf("----------------------------------------------\n");
            printf("client ip=%s,port=%d\n", cli_ip, ntohs(client_addr.sin_port));
            // ��������
            while ((recv_len = recv(connfd, recv_buf, sizeof(recv_buf), 0)) > 0)
            {
                printf("recv_buf: %s\n", recv_buf); // ��ӡ����
                send(connfd, recv_buf, recv_len, 0); // ���ͻ��˻�����
            }

            printf("client_port %d closed!\n", ntohs(client_addr.sin_port));
            close(connfd);    //�ر��������׽���
            exit(0); //�ӽ��̽���
        }
        else if (pid > 0)      // ������
            close(connfd);    //�ر��������׽���
    }
    close(sockfd);
    return 0;
}