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
typedef struct _IP_HEADER             //IPͷ���壬��20���ֽ�
{
    char m_cVersionAndHeaderLen;     //�汾��Ϣ(ǰ4λ)��ͷ����(��4λ)
    char m_cTypeOfService;         // ��������8λ
    short m_sTotalLenOfPacket;    //���ݰ�����
    short m_sPacketID;      //���ݰ���ʶ
    short m_sSliceinfo;     //��Ƭʹ��
    char m_cTTL;       //���ʱ��
    char m_cTypeOfProtocol;    //Э������
    short m_sCheckSum;      //У���
    unsigned int m_uiSourIp;     //ԴIP��ַ
    unsigned int m_uiDestIp;    //Ŀ��IP��ַ
} IP_HEADER, *PIP_HEADER;

typedef struct _UDP_HEADER         // UDP�ײ����壬��8���ֽ�
{
    unsigned short m_usSourPort;    // Դ�˿ں�16bit
    unsigned short m_usDestPort;     // Ŀ�Ķ˿ں�16bit
    unsigned short m_usLength;     // ���ݰ�����16bit
    unsigned short m_usCheckSum;   // У���16bit
} UDP_HEADER, *PUDP_HEADER;

int main()
{
    int sockfd,size,ret;
    char on = 1;
    struct sockaddr_in saddr;
    struct sockaddr_in raddr;

    IP_HEADER iph;
    UDP_HEADER udph;

    //���õ�ַ��Ϣ��ip��Ϣ
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(8888); //����Ķ˿�����ν
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);

    //����udp ���׽���
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);//��ԭʼ�׽���ʹ��UDPЭ��
    if (sockfd < 0)
    {
        perror("socket failed");
        return -1;
    }
    //���ö˿ڸ���
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //�󶨵�ַ��Ϣ��ip��Ϣ
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        perror("sbind failed");
        return -1;
    }
    int  val = sizeof(struct sockaddr);
    //���տͻ��˷�������Ϣ
    while (1)
    {
        puts("waiting data");
        ret = recvfrom(sockfd, rbuf, 500, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
        if (ret < 0)
        {
            perror("recvfrom failed");
            return -1;
        }
        memcpy(&iph, rbuf, 20); //�ѻ�����ǰ20���ֽڿ�����iph��
        memcpy(&udph, rbuf + 20, 8); //��ip��ͷ���8�ֽڿ�����udph��

        int srcp = ntohs(udph.m_usSourPort);
        struct in_addr ias, iad;
        ias.s_addr = iph.m_uiSourIp;
        iad.s_addr = iph.m_uiDestIp;

        char dip[100];
        strcpy(dip, inet_ntoa(iad));
        printf("(sIp=%s,sPort=%d), \n(dIp=%s,dPort=%d)\n", inet_ntoa(ias), ntohs(udph.m_usSourPort), dip, ntohs(udph.m_usDestPort));
        printf("recv data:%s\n", rbuf + 28);
    }
    close(sockfd);//�ر�ԭʼ�׽���
    getchar();
    return 0;
}
