/*ʹ��select���������Է������ķ�ʽ�Ͷ��socketͨ�š�����ֻ����ʾselect������ʹ�ã���ʹĳ�����ӹر��Ժ�Ҳ�����޸ĵ�ǰ���������������ﵽ���ֵ�����ֹ����
1. ����ʹ����һ������fd��ͨ�ſ�ʼ�����Ҫͨ�ŵĶ��socket�����������������
2. ��������һ����sock_fd��socket�����������ڼ����˿ڡ�
3. ��sock_fd������fd�в�Ϊ0������������select�����ļ���fdsr��
4. ����fdsr�п��Խ������ݵ����ӡ������sock_fd�������������Ӽ��룬���¼������ӵ�socket���������õ�fd�� */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MYPORT 8888 //����ʱʹ�õĶ˿�
#define MAXCLINE 5 //���Ӷ����еĸ���
#define BUF_SIZE 200
int fd[MAXCLINE]; //���ӵ�fd
int conn_amount; //��ǰ��������
void showclient()
{
    int i;
    printf("client amount:%d\n", conn_amount);
    for (i = 0; i < MAXCLINE; i++)
        printf("[%d]:%d ", i, fd[i]);
    printf("\n\n");
}
int main(void)
{
    int sock_fd, new_fd; //�����׽��� �����׽���
    struct sockaddr_in server_addr; // �������ĵ�ַ��Ϣ
    struct sockaddr_in client_addr; //�ͻ��˵ĵ�ַ��Ϣ
    socklen_t sin_size;
    int yes = 1;
    char buf[BUF_SIZE];
    int ret;
    int i;
    //����sock_fd�׽���
    if ((sock_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
    {
        perror("setsockopt");
        exit(1);
    }
    //�����׽ӿڵ�ѡ�� SO_REUSEADDR ������ͬһ���˿������������Ķ��ʵ��
    // setsockopt�ĵڶ�������SOL SOCKET ָ��ϵͳ�У�����ѡ��ļ��� ��ͨ�׽���
    if (setsockopt(sock_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1)
    {
        perror("setsockopt error \n");
        exit(1);
    }

    server_addr.sin_family = AF_INET; //�����ֽ���
    server_addr.sin_port = htons(MYPORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;//ͨ��IP
    memset(server_addr.sin_zero, '\0', sizeof(server_addr.sin_zero));
    if (bind(sock_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
    {
        perror("bind error!\n");
        getchar();
        exit(1);
    }
    if (listen(sock_fd, MAXCLINE) == -1)
    {
        perror("listen error!\n");
        exit(1);
    }
    printf("listen port %d\n", MYPORT);
    fd_set fdsr; //�ļ����������Ķ���
    int maxsock;
    struct timeval tv;
    conn_amount = 0;
    sin_size = sizeof(client_addr);
    maxsock = sock_fd;
    while (1)
    {
        //��ʼ���ļ�����������
        FD_ZERO(&fdsr); //�����������
        FD_SET(sock_fd, &fdsr); //��sock_fd������������
        //��ʱ���趨
        tv.tv_sec = 30;
        tv.tv_usec = 0;
        //��ӻ������
        for (i = 0; i < MAXCLINE; i++)
        {
            if (fd[i] != 0)
            {
                FD_SET(fd[i], &fdsr);
            }
        }
        //����ļ������������������� ������Ӧ�Ĵ���ʵ��I/O�ĸ��� ���û�������ͨѶ
        ret = select(maxsock + 1, &fdsr, NULL, NULL, &tv);
        if (ret < 0) //û���ҵ���Ч������ ʧ��
        {
            perror("select error!\n");
            break;
        }
        else if (ret == 0)// ָ����ʱ�䵽��
        {
            printf("timeout \n");
            continue;
        }
        //ѭ���ж���Ч�������Ƿ������ݵ���
        for (i = 0; i < conn_amount; i++)
        {
            if (FD_ISSET(fd[i], &fdsr))
            {
                ret = recv(fd[i], buf, sizeof(buf), 0);
                if (ret <= 0) //�ͻ������ӹرգ�����ļ����������е���Ӧ��λ
                {
                    printf("client[%d] close\n", i);
                    close(fd[i]);
                    FD_CLR(fd[i], &fdsr);
                    fd[i] = 0;
                    conn_amount--;
                }
                //��������Ӧ�����ݷ��͹��� ��������Ӧ�Ĵ���
                else
                {
                    if (ret < BUF_SIZE)
                        memset(&buf[ret], '\0', 1);
                    printf("client[%d] send:%s\n", i, buf);
                    send(fd[i], buf, sizeof(buf), 0);//�����ȥ
                }
            }
        }
        if (FD_ISSET(sock_fd, &fdsr))
        {
            new_fd = accept(sock_fd, (struct sockaddr *)&client_addr, &sin_size);
            if (new_fd <= 0)
            {
                perror("accept error\n");
                continue;
            }
            //����µ�fd �������� �ж���Ч���������Ƿ�С�����������������С�ڵĻ����Ͱ��µ������׽��ּ��뼯��
            if (conn_amount < MAXCLINE)
            {
                for (i = 0; i < MAXCLINE; i++)
                {
                    if (fd[i] == 0)
                    {
                        fd[i] = new_fd;
                        break;
                    }
                }
                conn_amount++;
                printf("new connection client[%d]%s:%d\n", conn_amount, inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));
                if (new_fd > maxsock)
                    maxsock = new_fd;
            }
            else
            {
                printf("max connections arrive ,exit\n");
                send(new_fd, "bye", 4, 0);
                close(new_fd);
                continue;
            }
        }
        showclient();
    }

    for (i = 0; i < MAXCLINE; i++)
    {
        if (fd[i] != 0)
        {
            close(fd[i]);
        }
    }
    return 0;
}