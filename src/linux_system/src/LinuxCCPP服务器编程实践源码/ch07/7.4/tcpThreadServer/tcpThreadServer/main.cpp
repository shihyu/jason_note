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
函数名称：	void *client_process(void *arg)
函数功能：	线程函数,处理客户信息
函数参数：	已连接套接字
函数返回：	无
************************************************************************/
void *client_process(void *arg)
{
    int recv_len = 0;
    char recv_buf[1024] = "";	// 接收缓冲区
    long tmp = (long)arg;
    int connfd = (int)tmp; // 传过来的已连接套接字
    // 接收数据
    while ((recv_len = recv(connfd, recv_buf, sizeof(recv_buf), 0)) > 0)
    {
        printf("recv_buf: %s\n", recv_buf); // 打印数据
        send(connfd, recv_buf, recv_len, 0); // 给客户端回数据
    }
    printf("client closed!\n");
    close(connfd);	//关闭已连接套接字
    return 	NULL;
}

//===============================================================
// 语法格式：	void main(void)
// 实现功能：	主函数，建立一个TCP并发服务器
// 入口参数：	无
// 出口参数：	无
//===============================================================
int main()
{
    int sockfd = 0, connfd = 0,err_log = 0;
    char on = 1;
    struct sockaddr_in my_addr;	// 服务器地址结构体
    unsigned short port = 8888; // 监听端口
    pthread_t thread_id;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);   // 创建TCP套接字
    if (sockfd < 0)
    {
        perror("socket error");
        exit(-1);
    }
    bzero(&my_addr, sizeof(my_addr));	   // 初始化服务器地址
    my_addr.sin_family = AF_INET;
    my_addr.sin_port = htons(port);
    my_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    printf("Binding server to port %d\n", port);
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));	//端口复用
    err_log = bind(sockfd, (struct sockaddr*)&my_addr, sizeof(my_addr));// 绑定
    if (err_log != 0)
    {
        perror("bind");
        close(sockfd);
        getchar();
        exit(-1);
    }
    err_log = listen(sockfd, 10);	// 监听，套接字变被动
    if (err_log != 0)
    {
        perror("listen");
        close(sockfd);
        exit(-1);
    }

    while (1)
    {
        char cli_ip[INET_ADDRSTRLEN] = "";	   // 用于保存客户端IP地址
        struct sockaddr_in client_addr;		   // 用于保存客户端地址
        socklen_t cliaddr_len = sizeof(client_addr);   // 必须初始化!!!
        printf("Waiting client...\n");
        //获得一个已经建立的连接
        connfd = accept(sockfd, (struct sockaddr*)&client_addr, &cliaddr_len);
        if (connfd < 0)
        {
            perror("accept this time");
            continue;
        }
        // 打印客户端的 ip 和端口
        inet_ntop(AF_INET, &client_addr.sin_addr, cli_ip, INET_ADDRSTRLEN);
        printf("----------------------------------------------\n");
        printf("client ip=%s,port=%d\n", cli_ip, ntohs(client_addr.sin_port));
        if (connfd > 0)
        {
            //由于同一个进程内的所有线程共享内存和变量，因此在传递参数时需作特殊处理，值传递。
            pthread_create(&thread_id, NULL, client_process, (void *)connfd);  //创建线程
            pthread_detach(thread_id); // 线程分离，让子线程结束时自动回收资源
        }
    }
    close(sockfd);
    return 0;
}