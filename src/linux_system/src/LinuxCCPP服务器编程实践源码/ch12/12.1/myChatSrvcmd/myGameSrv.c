#include <stdio.h>

#include <stdlib.h>

#include <string.h>

#include <netinet/in.h>

#include <arpa/inet.h>

#include <sys/select.h>

#include "mylink.h"



#define MAXLINE 80

#define SERV_PORT 8000



#define CL_CMD_LOGIN 'l'

#define CL_CMD_REG 'r'

#define CL_CMD_CREATE 'c'

#define CL_CMD_GET_TABLE_LIST 'g'

#define CL_CMD_OFFLINE 'o'

#define CL_CMD_CREATE_IS_BUSY 'b'







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



    return 0;

}



//特别要注意分割处理后原字符串 str 会变，变成第一个子字符串

void GetItem(char str[], char item1[], char item2[])

{

    const char * split = ",";

    char * p;

    p = strtok(str, split);

    int i = 0;

    while (p != NULL)

    {

        printf("%s\n", p);

        if (i == 1) sprintf(item1, p);

        else if(i==2)   sprintf(item2, p);

        i++;

        p = strtok(NULL, split);

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

MYLINK myhead  ;		//创建创建棋局的人的头指针，初始化为NULL





int main(int argc, char *argv[])

{

    int i, maxi, maxfd,ret;

    int listenfd, connfd, sockfd;

    int nready, client[FD_SETSIZE];

    ssize_t n;



    char *p,szName[255]="",szPwd[128]="",repBuf[512]="",szCreatorIP[64]="";





    //两个集合

    fd_set rset, allset;



    char buf[MAXLINE];

    char str[INET_ADDRSTRLEN]; /* #define INET_ADDRSTRLEN 16 */

    socklen_t cliaddr_len;

    struct sockaddr_in cliaddr, servaddr;



    //创建套接字

    listenfd = socket(AF_INET, SOCK_STREAM, 0);



    //为了套接字马上能复用

    int val = 1;

    ret = setsockopt(listenfd,SOL_SOCKET,SO_REUSEADDR,(void *)&val,sizeof(int));



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

    puts("Game server is running...");

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



                        //判断数据库中是否注册过，即是否存在

                        if(IsExist(szName))

                        {

                            //再判断是否已经登录了

                            MYLINK *p = &myhead;

                            p=p->next;

                            while(p)

                            {

                                if(strcmp(p->usrName,szName)==0)//同名说明已经登录

                                {

                                    sprintf(repBuf,"l,hasLogined");

                                    break;

                                }

                                p=p->next;

                            }

                            if(!p)

                            {

                                AppendNode(&myhead,connfd,szName,"");

                                sprintf(repBuf,"l,ok");

                            }

                        }

                        else sprintf(repBuf,"l,noexist");



                        write(sockfd, repBuf, strlen(repBuf));//回复客户端

                        break;

                    case CL_CMD_CREATE: //create game

                        printf("%s create game.",buf);

                        p = buf;

                        //得到游戏创建者的IP。

                        GetItem(p,szName,szCreatorIP);



                        //修改创建者标记

                        MYLINK *p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            if(strcmp(p->usrName,szName)==0)

                            {

                                p->isCreator=1;

                                p->isFree=1;

                                strcpy(p->creatorIP,szCreatorIP);

                                break;

                            }

                            p=p->next;

                        }

                        sprintf(repBuf,"c,ok,%s",buf+2);

                        //群发

                        p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            write(p->fd, repBuf, strlen(repBuf));

                            p=p->next;

                        }

                        break;



                    case CL_CMD_GET_TABLE_LIST:

                        sprintf(repBuf,"%c",CL_CMD_GET_TABLE_LIST);

                        GetAllFreeCreators(&myhead,repBuf+1);//得到所有空闲创建者列表

                        write(sockfd, repBuf, strlen(repBuf));//回复客户端

                        break;



                    case CL_CMD_CREATE_IS_BUSY:

                        GetName(buf,szName);

                        p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            if(strcmp(szName,p->usrName)==0)

                            {

                                p->isFree=0;

                                break;

                            }

                            p=p->next;

                        }

                        //更新空闲棋局列表，通知到大厅，让所有客户端玩家知道当前的空闲棋局

                        sprintf(repBuf,"%c",CL_CMD_GET_TABLE_LIST);

                        GetAllFreeCreators(&myhead,repBuf+1);



                        //群发

                        p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            write(p->fd, repBuf, strlen(repBuf));

                            p=p->next;

                        }

                        break;

                    case CL_CMD_OFFLINE:

                        DelNode(&myhead,buf+2); //在链表中删除该节点

                        //更新空闲棋局列表，通知到大厅，让所有客户端玩家知道当前的空闲棋局

                        sprintf(repBuf,"%c",CL_CMD_GET_TABLE_LIST);

                        GetAllFreeCreators(&myhead,repBuf+1);



                        //群发

                        p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            write(p->fd, repBuf, strlen(repBuf));

                            p=p->next;

                        }

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



