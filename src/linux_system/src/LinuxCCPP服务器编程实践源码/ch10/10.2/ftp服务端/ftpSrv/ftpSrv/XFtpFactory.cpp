#include "XFtpFactory.h"
#include "XFtpServerCMD.h"
#include "XFtpUSER.h"
#include "XFtpLIST.h"
#include "XFtpPORT.h"
#include "XFtpRETR.h"
#include "XFtpSTOR.h"
#include "testUtil.h"


XTask *XFtpFactory::CreateTask() {
    testout("At XFtpFactory::CreateTask");
    XFtpServerCMD *x = new XFtpServerCMD();

    x->Reg("USER", new XFtpUSER());

    x->Reg("PORT", new XFtpPORT());

    XFtpTask *list = new XFtpLIST();
    x->Reg("PWD", list);
    x->Reg("LIST", list);
    x->Reg("CWD", list);
    x->Reg("CDUP", list);

    x->Reg("RETR", new XFtpRETR());

    x->Reg("STOR", new XFtpSTOR());

    return x;
}

XFtpFactory::XFtpFactory() {

}