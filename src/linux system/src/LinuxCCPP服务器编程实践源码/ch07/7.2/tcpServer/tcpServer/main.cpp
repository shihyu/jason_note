#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#define  BUF_SIZE  200
#define PORT 8888

int main()
{
    struct   sockaddr_in fsin;
    int       clisock,alen, connum = 0, len, s;
    char     buf[BUF_SIZE] = "hi,client", rbuf[BUF_SIZE];
    struct  servent  *pse;    /* server information    */
    struct  protoent *ppe;    /* proto information     */
    struct sockaddr_in sin;   /* endpoint IP address   */

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = INADDR_ANY;
    sin.sin_port = htons(PORT);

    s = socket(PF_INET, SOCK_STREAM, 0);
    if (s == -1)
    {
        printf("creat socket error \n");
        getchar();
        return -1;
    }
    if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) == -1)
    {
        printf("socket bind error \n");
        getchar();
        return -1;
    }
    if (listen(s, 10) == -1)
    {
        printf("  socket listen error \n");
        getchar();
        return -1;
    }
    while (1)
    {
        alen = sizeof(struct sockaddr);
        puts("waiting client...");
        clisock = accept(s, (struct sockaddr *)&fsin,(socklen_t*)&alen);
        if (clisock == -1)
        {
            printf("accept failed\n");
            getchar();
            return -1;
        }
        connum++;
        printf("%d  client  comes\n", connum);
        len = recv(clisock, rbuf, sizeof(rbuf), 0);
        if (len < 0) perror("recv failed");
        sprintf(buf,"Server has received your data(%s).", rbuf);
        send(clisock, buf, strlen(buf), 0);
        close(clisock);
    }
    return 0;
}
