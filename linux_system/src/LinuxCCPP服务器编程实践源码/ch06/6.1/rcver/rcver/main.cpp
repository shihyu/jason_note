#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
char rbuf[500];
typedef struct _IP_HEADER             //IP头定义，共20个字节
{
    char m_cVersionAndHeaderLen;     //版本信息(前4位)，头长度(后4位)
    char m_cTypeOfService;         // 服务类型8位
    short m_sTotalLenOfPacket;    //数据包长度
    short m_sPacketID;      //数据包标识
    short m_sSliceinfo;     //分片使用
    char m_cTTL;       //存活时间
    char m_cTypeOfProtocol;    //协议类型
    short m_sCheckSum;      //校验和
    unsigned int m_uiSourIp;     //源IP地址
    unsigned int m_uiDestIp;    //目的IP地址
} IP_HEADER, *PIP_HEADER;

typedef struct _UDP_HEADER         // UDP首部定义，共8个字节
{
    unsigned short m_usSourPort;    // 源端口号16bit
    unsigned short m_usDestPort;     // 目的端口号16bit
    unsigned short m_usLength;     // 数据包长度16bit
    unsigned short m_usCheckSum;   // 校验和16bit
} UDP_HEADER, *PUDP_HEADER;

int main()
{
    int sockfd,size,ret;
    char on = 1;
    struct sockaddr_in saddr;
    struct sockaddr_in raddr;

    IP_HEADER iph;
    UDP_HEADER udph;

    //设置地址信息，ip信息
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(8888); //这里的端口无所谓
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);

    //创建udp 的套接字
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);//该原始套接字使用UDP协议
    if (sockfd < 0)
    {
        perror("socket failed");
        return -1;
    }
    //设置端口复用
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //绑定地址信息，ip信息
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        perror("sbind failed");
        return -1;
    }
    int  val = sizeof(struct sockaddr);
    //接收客户端发来的消息
    while (1)
    {
        puts("waiting data");
        ret = recvfrom(sockfd, rbuf, 500, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
        if (ret < 0)
        {
            perror("recvfrom failed");
            return -1;
        }
        memcpy(&iph, rbuf, 20); //把缓冲区前20个字节拷贝到iph中
        memcpy(&udph, rbuf + 20, 8); //把ip包头后的8字节拷贝到udph中

        int srcp = ntohs(udph.m_usSourPort);
        struct in_addr ias, iad;
        ias.s_addr = iph.m_uiSourIp;
        iad.s_addr = iph.m_uiDestIp;

        char dip[100];
        strcpy(dip, inet_ntoa(iad));
        printf("(sIp=%s,sPort=%d), \n(dIp=%s,dPort=%d)\n", inet_ntoa(ias), ntohs(udph.m_usSourPort), dip, ntohs(udph.m_usDestPort));
        printf("recv data:%s\n", rbuf + 28);
    }
    close(sockfd);//关闭原始套接字
    getchar();
    return 0;
}
