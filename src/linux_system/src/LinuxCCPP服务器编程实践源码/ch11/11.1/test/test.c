#include <stdio.h>
#include <string.h>
#include <mysql.h>

int main()
{
    MYSQL mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    char *query;
    int flag, t;

    /*����֮ǰ������mysql_init��ʼ��MYSQL���Ӿ��*/
    mysql_init(&mysql);
    /*ʹ��mysql_real_connect����server,�䅢������ΪMYSQL�����serverIP��ַ��
    ��¼mysql��username��password��Ҫ���ӵ����ݿ��*/
    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "test", 0, NULL, 0))
        printf("Error connecting to Mysql!\n");
    else
        printf("Connected Mysql successful!\n");


    query = "select * from student";
    /*��ѯ���ɹ��򷵻�0*/
    flag = mysql_real_query(&mysql, query, (unsigned int)strlen(query));
    if(flag) {
        printf("Query failed!\n");
        return 0;
    } else {
        printf("[%s] made...\n", query);
    }


    /*mysql_store_result�����еĲ�ѯ�����ȡ��client*/
    res = mysql_store_result(&mysql);
    /*mysql_fetch_row�������������һ��*/
    do
    {
        row = mysql_fetch_row(res);
        if (row == 0)break;
        /*mysql_num_fields���ؽ�����е��ֶ���Ŀ*/
        for (t = 0; t < mysql_num_fields(res); t++)
        {
            printf("%s\t", row[t]);
        }
        printf("\n");
    } while (1);

    /*�ر�����*/
    mysql_close(&mysql);
    return 0;
}