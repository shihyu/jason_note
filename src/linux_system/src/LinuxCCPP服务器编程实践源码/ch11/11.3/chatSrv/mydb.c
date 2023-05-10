#include <stdio.h>
#include <string.h>
#include <mysql.h>
#include <time.h>



int insert(char szName[])
{
    MYSQL mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    char *query;
    int r, t,id=12;
    char buf[512] = "", cur_time[55] = "";
    mysql_init(&mysql);
    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "chatdb", 0, NULL, 0))
    {
        printf("Failed to connect to Mysql!\n");
        return 0;
    }
    else  printf("Connected to Mysql successfully!\n");

    sprintf(buf, "INSERT INTO qqnum(name) VALUES(\'%s\')", szName);
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

int IsExist(char szName[])
{
    MYSQL mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    char *query;
    int r, t,id=12;
    char buf[512] = "", cur_time[55] = "";
    mysql_init(&mysql);
    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "chatdb", 0, NULL, 0))
    {
        printf("Failed to connect to Mysql!\n");
        res = -1;
        goto end;
    }
    else  printf("Connected to Mysql successfully!\n");


    //sprintf(buf, "INSERT INTO qqnum(name) VALUES(\'%s\')", szName);
    sprintf(buf, "select name from qqnum where name ='%s'", szName);

    //r = mysql_query(&mysql, buf);
//	if (mysql_query(&mysql, "SELECT name FROM qqnum WHERE name='aa44'"))
    if (mysql_query(&mysql, buf))
    {
        res =-1;
        goto end;
    }

    MYSQL_RES *result = mysql_store_result(&mysql);
    if (result == NULL)
    {
        res =-1;
        goto end;
    }
    MYSQL_FIELD *field;
    row = mysql_fetch_row(result);
    if(row>0)
    {
        printf("%s\n", row[0]);
        res = 1;
        goto end;
    }
    else res = 0;//不存在


end:
    mysql_close(&mysql);
    return res;
}

int showTable()
{
    MYSQL mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    char *query;
    int flag, t;

    /*连接之前。先用mysql_init初始化MYSQL连接句柄*/
    mysql_init(&mysql);
    /*使用mysql_real_connect连接server,其參数依次为MYSQL句柄。serverIP地址。
    登录mysql的username，password，要连接的数据库等*/
    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "chatdb", 0, NULL, 0))
        printf("Error connecting to Mysql!\n");
    else
        printf("Connected Mysql successful!\n");


    query = "select * from qqnum";
    /*查询，成功则返回0*/
    flag = mysql_real_query(&mysql, query, (unsigned int)strlen(query));
    if(flag) {
        printf("Query failed!\n");
        return 0;
    } else {
        printf("[%s] made...\n", query);
    }

    /*mysql_store_result讲所有的查询结果读取到client*/
    res = mysql_store_result(&mysql);
    /*mysql_fetch_row检索结果集的下一行*/
    do
    {
        row = mysql_fetch_row(res);
        if (row == 0)break;
        /*mysql_num_fields返回结果集中的字段数目*/
        for (t = 0; t < mysql_num_fields(res); t++)
        {
            printf("%s\t", row[t]);
        }
        printf("\n");
    } while (1);

    /*关闭连接*/
    mysql_close(&mysql);
    return 0;
}