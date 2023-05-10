#include <stdio.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>

#define MAXLINE 80
#define SERV_PORT 8000

#define CL_CMD_REG 'r'
#define CL_CMD_LOGIN 'l'
#define CL_CMD_CHAT 'c'

int GetName(char str[],char szName[])
{
    //char str[] ="a,b,c,d*e";
    const char * split = ",";
    char * p;
    p = strtok (str,split);
    int i=0;
    while(p!=NULL)
    {
        printf ("%s\n",p);
        if(i==1) sprintf(szName,p);
        i++;
        p = strtok(NULL,split);
    }
}

//查找字符串中某个字符出现的次数
int countChar(const char *p, const char chr)
{
    int count = 0,i = 0;
    while(*(p+i))
    {
        if(p[i] == chr)//字符数组存放在一块内存区域中，按索引找字符，指针本身不变
            ++count;
        ++i;// 按数组的索引值找到对应指针变量的值
    }
    //printf("字符串中w出现的次数：%d",count);
    return count;
}


int main(int argc, char *argv[])
{
    int i, maxi, maxfd;
    int listenfd, connfd, sockfd;
    int nready, client[FD_SETSIZE];
    ssize_t n;

    char szName[255]="",szPwd[128]="",repBuf[512]="";


    //两个集合
    fd_set rset, allset;

    char buf[MAXLINE];
    char str[INET_ADDRSTRLEN]; /* #define INET_ADDRSTRLEN 16 */
    socklen_t cliaddr_len;
    struct sockaddr_in cliaddr, servaddr;

    //创建套接字
    listenfd = socket(AF_INET, SOCK_STREAM, 0);

    int val = 1;
    int ret = setsockopt(listenfd,SOL_SOCKET,SO_REUSEADDR,(void *)&val,sizeof(int));

    //绑定
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(SERV_PORT);


    bind(listenfd, (struct sockaddr *)&servaddr, sizeof(servaddr));

    //监听
    listen(listenfd, 20); /* 默认最大128 */

    //需要接收最大文件描述符
    maxfd = listenfd;

    //数组初始化为-1
    maxi = -1;
    for (i = 0; i < FD_SETSIZE; i++)
        client[i] = -1;

    //集合清零
    FD_ZERO(&allset);

    //将listenfd加入allset集合
    FD_SET(listenfd, &allset);

    puts("Chat server is running...");


    for (; ;)
    {
        //关键点3
        rset = allset; /* 每次循环时都重新设置select监控信号集 */

        //select返回rest集合中发生读事件的总数  参数1：最大文件描述符+1
        nready = select(maxfd + 1, &rset, NULL, NULL, NULL);
        if (nready < 0)
            puts("select error");

        //listenfd是否在rset集合中
        if (FD_ISSET(listenfd, &rset))
        {
            //accept接收
            cliaddr_len = sizeof(cliaddr);
            //accept返回通信套接字，当前非阻塞，因为select已经发生读写事件
            connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &cliaddr_len);



            printf("received from %s at PORT %d\n",
                   inet_ntop(AF_INET, &cliaddr.sin_addr, str, sizeof(str)),
                   ntohs(cliaddr.sin_port));

            //关键点1
            for (i = 0; i < FD_SETSIZE; i++)
                if (client[i] < 0)
                {
                    client[i] = connfd; /* 保存accept返回的通信套接字connfd存到client[]里 */
                    break;
                }

            /* 是否达到select能监控的文件个数上限 1024 */
            if (i == FD_SETSIZE) {
                fputs("too many clients\n", stderr);
                exit(1);
            }

            //关键点2
            FD_SET(connfd, &allset); /*添加一个新的文件描述符到监控信号集里 */

            //更新最大文件描述符数
            if (connfd > maxfd)
                maxfd = connfd; /* select第一个参数需要 */
            if (i > maxi)
                maxi = i; /* 更新client[]最大下标值 */

            /* 如果没有更多的就绪文件描述符继续回到上面select阻塞监听,负责处理未处理完的就绪文件描述符 */
            if (--nready == 0)
                continue;
        }

        for (i = 0; i <= maxi; i++)
        {
            //检测clients 哪个有数据就绪
            if ((sockfd = client[i]) < 0)
                continue;

            //sockfd（connd）是否在rset集合中
            if (FD_ISSET(sockfd, &rset))
            {
                //进行读数据 不用阻塞立即读取（select已经帮忙处理阻塞环节）
                if ((n = read(sockfd, buf, MAXLINE)) == 0)
                {
                    /* 无数据情况 client关闭链接，服务器端也关闭对应链接 */
                    close(sockfd);
                    FD_CLR(sockfd, &allset); /*解除select监控此文件描述符 */
                    client[i] = -1;
                }
                else
                {
                    char code= buf[0];
                    switch(code)
                    {
                    case CL_CMD_REG:   //注册命令处理
                        if(1!=countChar(buf,','))
                        {
                            puts("invalid protocal!");
                            break;
                        }

                        GetName(buf,szName);

                        //判断名字是否重复
                        if(IsExist(szName))
                        {
                            sprintf(repBuf,"r,exist");
                        }
                        else
                        {
                            insert(szName);
                            showTable();
                            sprintf(repBuf,"r,ok");
                            printf("reg ok,%s\n",szName);
                        }
                        write(sockfd, repBuf, strlen(repBuf));//回复客户端

                        break;
                    case CL_CMD_LOGIN: //登录命令处理
                        if(1!=countChar(buf,','))
                        {
                            puts("invalid protocal!");
                            break;
                        }

                        GetName(buf,szName);

                        //判断是否注册过，即是否存在
                        if(IsExist(szName))
                        {
                            sprintf(repBuf,"l,ok");
                            printf("login ok,%s\n",szName);
                        }
                        else sprintf(repBuf,"l,noexist");
                        write(sockfd, repBuf, strlen(repBuf));//回复客户端
                        break;
                    case CL_CMD_CHAT://聊天命令处理
                        puts("send all");

                        //群发
                        for(i=0; i<=maxi; i++)
                            if(client[i]!=-1)
                                write(client[i], buf+2, n);//写回客户端，+2表示去掉命令头(c,)，这样只发送聊天内容
                        break;
                    }//switch





                }
                if (--nready == 0)
                    break;
            }
        }

    }
    close(listenfd);
    return 0;
}
