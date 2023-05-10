#include <cstdio>


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

/************************************************************************
�������ƣ�	void *client_process(void *arg)
�������ܣ�	�̺߳���,����ͻ���Ϣ
����������	�������׽���
�������أ�	��
************************************************************************/
void *client_process(void *arg)
{
    int recv_len = 0;
    char recv_buf[1024] = "";	// ���ջ�����
    long tmp = (long)arg;
    int connfd = (int)tmp; // ���������������׽���
    // ��������
    while ((recv_len = recv(connfd, recv_buf, sizeof(recv_buf), 0)) > 0)
    {
        printf("recv_buf: %s\n", recv_buf); // ��ӡ����
        send(connfd, recv_buf, recv_len, 0); // ���ͻ��˻�����
    }
    printf("client closed!\n");
    close(connfd);	//�ر��������׽���
    return 	NULL;
}

//===============================================================
// �﷨��ʽ��	void main(void)
// ʵ�ֹ��ܣ�	������������һ��TCP����������
// ��ڲ�����	��
// ���ڲ�����	��
//===============================================================
int main()
{
    int sockfd = 0, connfd = 0,err_log = 0;
    char on = 1;
    struct sockaddr_in my_addr;	// ��������ַ�ṹ��
    unsigned short port = 8888; // �����˿�
    pthread_t thread_id;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);   // ����TCP�׽���
    if (sockfd < 0)
    {
        perror("socket error");
        exit(-1);
    }
    bzero(&my_addr, sizeof(my_addr));	   // ��ʼ����������ַ
    my_addr.sin_family = AF_INET;
    my_addr.sin_port = htons(port);
    my_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    printf("Binding server to port %d\n", port);
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));	//�˿ڸ���
    err_log = bind(sockfd, (struct sockaddr*)&my_addr, sizeof(my_addr));// ��
    if (err_log != 0)
    {
        perror("bind");
        close(sockfd);
        getchar();
        exit(-1);
    }
    err_log = listen(sockfd, 10);	// �������׽��ֱ䱻��
    if (err_log != 0)
    {
        perror("listen");
        close(sockfd);
        exit(-1);
    }

    while (1)
    {
        char cli_ip[INET_ADDRSTRLEN] = "";	   // ���ڱ���ͻ���IP��ַ
        struct sockaddr_in client_addr;		   // ���ڱ���ͻ��˵�ַ
        socklen_t cliaddr_len = sizeof(client_addr);   // �����ʼ��!!!
        printf("Waiting client...\n");
        //���һ���Ѿ�����������
        connfd = accept(sockfd, (struct sockaddr*)&client_addr, &cliaddr_len);
        if (connfd < 0)
        {
            perror("accept this time");
            continue;
        }
        // ��ӡ�ͻ��˵� ip �Ͷ˿�
        inet_ntop(AF_INET, &client_addr.sin_addr, cli_ip, INET_ADDRSTRLEN);
        printf("----------------------------------------------\n");
        printf("client ip=%s,port=%d\n", cli_ip, ntohs(client_addr.sin_port));
        if (connfd > 0)
        {
            //����ͬһ�������ڵ������̹߳����ڴ�ͱ���������ڴ��ݲ���ʱ�������⴦��ֵ���ݡ�
            pthread_create(&thread_id, NULL, client_process, (void *)connfd);  //�����߳�
            pthread_detach(thread_id); // �̷߳��룬�����߳̽���ʱ�Զ�������Դ
        }
    }
    close(sockfd);
    return 0;
}