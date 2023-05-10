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



//�ر�Ҫע��ָ���ԭ�ַ��� str ��䣬��ɵ�һ�����ַ���

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



//�����ַ�����ĳ���ַ����ֵĴ���

int countChar(const char *p, const char chr)

{

    int count = 0,i = 0;

    while(*(p+i))

    {

        if(p[i] == chr)//�ַ���������һ���ڴ������У����������ַ���ָ�뱾����

            ++count;

        ++i;// �����������ֵ�ҵ���Ӧָ�������ֵ

    }

    //printf("�ַ�����w���ֵĴ�����%d",count);

    return count;

}

MYLINK myhead  ;		//����������ֵ��˵�ͷָ�룬��ʼ��ΪNULL





int main(int argc, char *argv[])

{

    int i, maxi, maxfd,ret;

    int listenfd, connfd, sockfd;

    int nready, client[FD_SETSIZE];

    ssize_t n;



    char *p,szName[255]="",szPwd[128]="",repBuf[512]="",szCreatorIP[64]="";





    //��������

    fd_set rset, allset;



    char buf[MAXLINE];

    char str[INET_ADDRSTRLEN]; /* #define INET_ADDRSTRLEN 16 */

    socklen_t cliaddr_len;

    struct sockaddr_in cliaddr, servaddr;



    //�����׽���

    listenfd = socket(AF_INET, SOCK_STREAM, 0);



    //Ϊ���׽��������ܸ���

    int val = 1;

    ret = setsockopt(listenfd,SOL_SOCKET,SO_REUSEADDR,(void *)&val,sizeof(int));



    //��

    bzero(&servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;

    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);

    servaddr.sin_port = htons(SERV_PORT);





    bind(listenfd, (struct sockaddr *)&servaddr, sizeof(servaddr));



    //����

    listen(listenfd, 20); /* Ĭ�����128 */



    //��Ҫ��������ļ�������

    maxfd = listenfd;



    //�����ʼ��Ϊ-1

    maxi = -1;

    for (i = 0; i < FD_SETSIZE; i++)

        client[i] = -1;



    //��������

    FD_ZERO(&allset);



    //��listenfd����allset����

    FD_SET(listenfd, &allset);

    puts("Game server is running...");

    for (; ;)

    {

        //�ؼ���3

        rset = allset; /* ÿ��ѭ��ʱ����������select����źż� */



        //select����rest�����з������¼�������  ����1������ļ�������+1

        nready = select(maxfd + 1, &rset, NULL, NULL, NULL);

        if (nready < 0)

            puts("select error");





        //listenfd�Ƿ���rset������

        if (FD_ISSET(listenfd, &rset))

        {

            //accept����

            cliaddr_len = sizeof(cliaddr);

            //accept����ͨ���׽��֣���ǰ����������Ϊselect�Ѿ�������д�¼�

            connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &cliaddr_len);





            printf("received from %s at PORT %d\n",

                   inet_ntop(AF_INET, &cliaddr.sin_addr, str, sizeof(str)),

                   ntohs(cliaddr.sin_port));





            //�ؼ���1

            for (i = 0; i < FD_SETSIZE; i++)

                if (client[i] < 0)

                {

                    client[i] = connfd; /* ����accept���ص�ͨ���׽���connfd�浽client[]�� */

                    break;

                }



            /* �Ƿ�ﵽselect�ܼ�ص��ļ��������� 1024 */

            if (i == FD_SETSIZE) {

                fputs("too many clients\n", stderr);

                exit(1);

            }



            //�ؼ���2

            FD_SET(connfd, &allset); /*���һ���µ��ļ�������������źż��� */



            //��������ļ���������

            if (connfd > maxfd)

                maxfd = connfd; /* select��һ��������Ҫ */

            if (i > maxi)

                maxi = i; /* ����client[]����±�ֵ */



            /* ���û�и���ľ����ļ������������ص�����select��������,������δ������ľ����ļ������� */

            if (--nready == 0)

                continue;

        }



        for (i = 0; i <= maxi; i++)

        {

            //���clients �ĸ������ݾ���

            if ((sockfd = client[i]) < 0)

                continue;



            //sockfd��connd���Ƿ���rset������

            if (FD_ISSET(sockfd, &rset))

            {

                //���ж����� ��������������ȡ��select�Ѿ���æ�����������ڣ�

                if ((n = read(sockfd, buf, MAXLINE)) == 0)

                {

                    /* ��������� client�ر����ӣ���������Ҳ�رն�Ӧ���� */

                    close(sockfd);

                    FD_CLR(sockfd, &allset); /*���select��ش��ļ������� */

                    client[i] = -1;

                }

                else

                {

                    char code= buf[0];

                    switch(code)

                    {

                    case CL_CMD_REG:   //ע�������

                        if(1!=countChar(buf,','))

                        {

                            puts("invalid protocal!");

                            break;

                        }



                        GetName(buf,szName);



                        //�ж������Ƿ��ظ�

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

                        write(sockfd, repBuf, strlen(repBuf));//�ظ��ͻ���



                        break;

                    case CL_CMD_LOGIN: //��¼�����

                        if(1!=countChar(buf,','))

                        {

                            puts("invalid protocal!");

                            break;

                        }



                        GetName(buf,szName);



                        //�ж����ݿ����Ƿ�ע��������Ƿ����

                        if(IsExist(szName))

                        {

                            //���ж��Ƿ��Ѿ���¼��

                            MYLINK *p = &myhead;

                            p=p->next;

                            while(p)

                            {

                                if(strcmp(p->usrName,szName)==0)//ͬ��˵���Ѿ���¼

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



                        write(sockfd, repBuf, strlen(repBuf));//�ظ��ͻ���

                        break;

                    case CL_CMD_CREATE: //create game

                        printf("%s create game.",buf);

                        p = buf;

                        //�õ���Ϸ�����ߵ�IP��

                        GetItem(p,szName,szCreatorIP);



                        //�޸Ĵ����߱��

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

                        //Ⱥ��

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

                        GetAllFreeCreators(&myhead,repBuf+1);//�õ����п��д������б�

                        write(sockfd, repBuf, strlen(repBuf));//�ظ��ͻ���

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

                        //���¿�������б�֪ͨ�������������пͻ������֪����ǰ�Ŀ������

                        sprintf(repBuf,"%c",CL_CMD_GET_TABLE_LIST);

                        GetAllFreeCreators(&myhead,repBuf+1);



                        //Ⱥ��

                        p = &myhead;

                        p=p->next;

                        while(p)

                        {

                            write(p->fd, repBuf, strlen(repBuf));

                            p=p->next;

                        }

                        break;

                    case CL_CMD_OFFLINE:

                        DelNode(&myhead,buf+2); //��������ɾ���ýڵ�

                        //���¿�������б�֪ͨ�������������пͻ������֪����ǰ�Ŀ������

                        sprintf(repBuf,"%c",CL_CMD_GET_TABLE_LIST);

                        GetAllFreeCreators(&myhead,repBuf+1);



                        //Ⱥ��

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



