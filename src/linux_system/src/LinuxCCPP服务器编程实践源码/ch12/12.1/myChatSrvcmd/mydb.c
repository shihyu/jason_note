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

    else res = 0;//������





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



    /*����֮ǰ������mysql_init��ʼ��MYSQL���Ӿ��*/

    mysql_init(&mysql);

    /*ʹ��mysql_real_connect����server,�䅢������ΪMYSQL�����serverIP��ַ��

    ��¼mysql��username��password��Ҫ���ӵ����ݿ��*/

    if (!mysql_real_connect(&mysql, "localhost", "root", "123456", "chatdb", 0, NULL, 0))

        printf("Error connecting to Mysql!\n");

    else

        printf("Connected Mysql successful!\n");





    query = "select * from qqnum";

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