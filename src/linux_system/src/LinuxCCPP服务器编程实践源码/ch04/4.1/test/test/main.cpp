#include <cstdio>
#include <arpa/inet.h>
int main()
{
    struct in_addr ia;

    in_addr_t dwIP = inet_addr("172.16.2.6");
    ia.s_addr = dwIP;
    printf("ia.s_addr=0x%x\n", ia.s_addr);
    printf("real_ip=%s\n", inet_ntoa(ia));
    return 0;
}