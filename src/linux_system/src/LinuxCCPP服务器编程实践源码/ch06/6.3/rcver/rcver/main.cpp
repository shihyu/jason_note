#include <stdio.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>//for inet_ntoa
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <linux/if_ether.h>
#include <net/if.h>
#include <unistd.h>//for close
#include <string.h>
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

typedef struct _UDP_HEADER         // UDP头定义，共8个字节
{
    unsigned short m_usSourPort;    // 源端口号16bit
    unsigned short m_usDestPort;     // 目的端口号16bit
    unsigned short m_usLength;     // 数据包长度16bit
    unsigned short m_usCheckSum;   // 校验和16bit
} UDP_HEADER, *PUDP_HEADER;

int main(int argc, char **argv) {
    int sock, n;
    char buffer[2048];
    unsigned char *iphead, *ethhead;

    struct sockaddr_in saddr;
    struct sockaddr_in raddr;
    IP_HEADER iph;
    UDP_HEADER udph;


    if ((sock = socket(PF_PACKET, SOCK_RAW,htons(ETH_P_IP))) < 0) { //htons(ETH_P_ALL)
        perror("socket");
        return -1;
    }
    long long cn = 1;
    while (1) {
        n = recvfrom(sock, buffer, 2048, 0, NULL, NULL);
        /* Check to see if the packet contains at least
         * complete Ethernet (14), IP (20) and TCP/UDP
         * (8) headers.
         */
        if (n < 42) {
            perror("recvfrom():");
            printf("Incomplete packet (errno is %d)\n",errno);
            close(sock);
            return -1;
        }

        ethhead = (unsigned char*)buffer;
        /*
        printf("Source MAC address: "
        	"%02x:%02x:%02x:%02x:%02x:%02x\n",
        	ethhead[0], ethhead[1], ethhead[2],
        	ethhead[3], ethhead[4], ethhead[5]);
        printf("Destination MAC address: "
        	"%02x:%02x:%02x:%02x:%02x:%02x\n",
        	ethhead[6], ethhead[7], ethhead[8],
        	ethhead[9], ethhead[10], ethhead[11]);
        	*/
        iphead = ethhead + 14; /* Skip Ethernet header */
        if (*iphead == 0x45) {
            /* Double check for IPv4
            					  * and no options present */
            //printf("Layer-4 protocol %d,", iphead[9]);
            memcpy(&iph, iphead, 20);
            if (iphead[12] == iphead[16] && iphead[13] == iphead[17] && iphead[14] == iphead[18] && iphead[15] == iphead[19])
                continue;
            if (iphead[12] == 127)
                continue;
            printf("-----cn=%ld-----\n", cn++);
            printf("%d bytes read\n", n);
            /*这样也可以得到IP和端口
            printf("Source host %d.%d.%d.%d\n",iphead[12], iphead[13],
            	iphead[14], iphead[15]);
            printf("Dest host %d.%d.%d.%d\n",iphead[16], iphead[17],
            	iphead[18], iphead[19]);
            		*/

            struct in_addr ias, iad;
            ias.s_addr = iph.m_uiSourIp;
            iad.s_addr = iph.m_uiDestIp;
            char dip[100];
            strcpy(dip, inet_ntoa(iad));
            printf("sIp=%s,   dIp=%s, \n", inet_ntoa(ias), dip);

            //printf("Layer-4 protocol %d,", iphead[9]);//如果需要，可以打印下协议号
            if (IPPROTO_ICMP == iphead[9]) puts("Receive ICMP package.");
            if (IPPROTO_UDP == iphead[9])
            {
                memcpy(&udph, iphead + 20, 8);//加20是越过IP首部
                printf("Source,Dest ports %d,%d\n", udph.m_usSourPort,udph.m_usDestPort);
                printf("Receive UDP package,data:%s\n", iphead + 28);//越过ip首部和udp首部
            }
            if (IPPROTO_TCP == iphead[9]) puts("Receive TCP package.");
        }
    }
}