#include <iostream>
#include <string>
#include <mylib/mylib.h>

int main() {
#ifdef HELLOCMAKE_VERSION
    std::cout << "version: " << HELLOCMAKE_VERSION << std::endl;
#else
    std::cout << "version undefined!" << std::endl;
#endif
    int cppver = __cplusplus;
    MyLib::getInstance().setSecret("!!!");
    std::string msg = "Hello, C++ version " + std::to_string(cppver);
    msg = MyLib::getInstance().doSomeJobs(msg);
    std::cout << "message: " << msg << std::endl;
    return 0;
}
