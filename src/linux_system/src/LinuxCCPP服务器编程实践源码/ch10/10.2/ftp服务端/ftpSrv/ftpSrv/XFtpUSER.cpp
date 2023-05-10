#include "XFtpUSER.h"
#include "testUtil.h"

void XFtpUSER::Parse(std::string, std::string) {
    testout("AT XFtpUSER::Parse");
    ResCMD("230 Login successsful.\r\n");
}
