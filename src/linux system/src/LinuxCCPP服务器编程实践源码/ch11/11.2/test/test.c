#include <stdio.h>
#include <string.h>
#include <mysql.h>
#include <time.h>

int
GetDateTime(char * psDateTime) {
    time_t nSeconds;
    struct tm * pTM;

    time(&nSeconds);
    pTM = localtime(&nSeconds);

    /* ϵͳ���ں�ʱ��,��ʽ: yyyymmddHHMMSS */
    sprintf(psDateTime,
            "%04d-%02d-%02d %02d:%02d:%02d",
            pTM->tm_year + 1900,
            pTM->tm_mon + 1,
            pTM->tm_mday,
            pTM->tm_hour,
            pTM->tm_min,
            pTM->tm_sec);

    return 0;
}

int insert()
{
    MYSQL mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    char *query;
    int r, t;
    char buf[512] = "", cur_time[55] = "", szName[100] = "Jack2";
    mysql_init(&mysql);
    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "test", 0, NULL, 0))
    {
        printf("Failed to connect to Mysql!\n");
        return 0;
    }
    else  printf("Connected to Mysql successfully!\n");

    GetDateTime(cur_time);
    sprintf(buf, "INSERT INTO student(name,age,SETTIME) VALUES(\'%s\',%d,\'%s\')", szName, 27, cur_time);
    r = mysql_query(&mysql, buf);

    if (r) {
        printf("Insert data failure!\n");
        return 0;
    }
    else {
        printf("Insert data success!\n");
    }
    mysql_close(&mysql);
    return 0;
}


void main()
{
    insert();
    showTable();
}
int showTable()
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