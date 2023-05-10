#include <iostream>
using namespace std;

int main()
{
    cout << "Content-Type: text/html\n\n";  //注意结尾是两个\n
    cout << "<html>\n";
    cout << "<head>\n";
    cout << "<title>Hello World - First CGI Program</title>\n";
    cout << "</head>\n";
    cout << "<body bgcolor=\"yellow\">\n";
    cout << "<h2> <font color=\"#FF0000\">Hello World! This is my first CGI program</font></h2>\n";
    cout << "</body>\n";
    cout << "</html>\n";

    return 0;
}
