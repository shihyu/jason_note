#include "stdio.h"

#include "mylink.h"









void AppendNode(struct link *head,int fd,char szName[],char ip[]) {   //声明创建节点函数

    struct link *p = NULL,*pr = head;      //创建p指针，初始化为NULL；创建pr指针，通过pr指针来给指针域赋值



    p = (struct link *)malloc(sizeof(struct link)) ; //为指针p申请内存空间，必须操作，因为p是新创建的节点

    if(p == NULL) {			//如果申请内存失败，则退出程序

        printf("NO enough momery to allocate!\n");

        exit(0);

    }

    if(head == NULL) {		//如果头指针为NULL,说明现在链表是空表

        head = p;								//使head指针指向p的地址(p已经通过malloc申请了内存，所以有地址）

    } else {										//此时链表已经有头节点 ，再一次执行了AppendNode函数

        //注：假如这是第二次添加节点

        //因为第一次添加头节点时，pr = head，和头指针一样指向头节点的地址

        while(pr->next!= NULL) {		//当pr指向的地址，即此时的p的指针域不为NULL(即p不是尾节点)

            pr = pr->next;	//使pr指向头节点的指针域

        }

        pr->next = p;	//使pr的指针域指向新键节点的地址，此时的next指针域是头节点的指针域

    }



    p->fd = fd; 			//给p的数据域赋值

    sprintf(p->usrName,"%s",szName);

    sprintf(p->creatorIP,"%s",ip);

    p->isFree=1;

    p->isCreator=0;

    p->next = NULL;			//新添加的节点位于表尾，所以它的指针域为NULL

}





void DelNode(struct link *head, char szName[]) {

    struct link *p = NULL,*pre=head,*pr = head;

    while(pr->next!= NULL) {

        pre=pr;

        pr = pr->next;

        if(strcmp(pr->usrName,szName)==0)

        {

            pre->next=pr->next;

            free(pr);

            break;

        }

    }

}



void DisplayNode(struct link *head) {         	//输出函数，打印链表

    struct link *p = head->next;			// 定义p指针使其指向头节点

    int j = 1;									//定义j记录这是第几个数值

    while(p != NULL) {		//因为p = p->next,所以直到尾节点打印结束

        printf("%5d%10d\n",j,p->fd);

        p = p->next;		//因为节点已经创建成功，所以p的指向由头节点指向下一个节点(每一个节点的指针域都指向了下一个节点)

        j++;

    }

}



void GetAllFreeCreators(struct link *head,char *buf) {         	//输出函数，打印链表

    struct link *p = head->next;			// 定义p指针使其指向头节点



    while(p != NULL)

    {

        if(p->isCreator && p->isFree)

        {

            strcat(buf,",");//所有在线用户名之间用逗号隔开

            strcat(buf,p->usrName);

            strcat(buf,"(");

            strcat(buf,p->creatorIP);

            strcat(buf,")");

        }

        p = p->next;

    }

}





void DeleteMemory(struct link *head) {			//释放资源函数

    struct link *p = head->next,*pr = NULL;	        //定义p指针指向头节点

    while(p != NULL) {				//当p的指针域不为NULL

        pr = p;									//将每一个节点的地址赋值给pr指针

        p = p->next;			        //使p指向下一个节点

        free(pr);								//释放此时pr指向节点的内存

    }

}

