#include <cstdio>
#include <iostream>
#include<string.h>
using namespace std;
struct MyData
{
    int nLen;
    char data[0];
};
int main()
{
    int nLen = 10;
    char str[10] = "123456789";//�����ǻ���һ��'\0'��������10���ַ�Ŷ��

    cout << "Size of MyData: " << sizeof(MyData) << endl;
    MyData *myData = (MyData*)malloc(sizeof(MyData) + 10);
    memcpy(myData->data, str, 10);
    cout << "myData's Data is: " << myData->data << endl;
    cout << "Size of MyData: " << sizeof(MyData) << endl;
    free(myData);
    getchar();

    return 0;
}
