#include "stdio.h"

#include "mylink.h"









void AppendNode(struct link *head,int fd,char szName[],char ip[]) {   //���������ڵ㺯��

    struct link *p = NULL,*pr = head;      //����pָ�룬��ʼ��ΪNULL������prָ�룬ͨ��prָ������ָ����ֵ



    p = (struct link *)malloc(sizeof(struct link)) ; //Ϊָ��p�����ڴ�ռ䣬�����������Ϊp���´����Ľڵ�

    if(p == NULL) {			//��������ڴ�ʧ�ܣ����˳�����

        printf("NO enough momery to allocate!\n");

        exit(0);

    }

    if(head == NULL) {		//���ͷָ��ΪNULL,˵�����������ǿձ�

        head = p;								//ʹheadָ��ָ��p�ĵ�ַ(p�Ѿ�ͨ��malloc�������ڴ棬�����е�ַ��

    } else {										//��ʱ�����Ѿ���ͷ�ڵ� ����һ��ִ����AppendNode����

        //ע���������ǵڶ�����ӽڵ�

        //��Ϊ��һ�����ͷ�ڵ�ʱ��pr = head����ͷָ��һ��ָ��ͷ�ڵ�ĵ�ַ

        while(pr->next!= NULL) {		//��prָ��ĵ�ַ������ʱ��p��ָ����ΪNULL(��p����β�ڵ�)

            pr = pr->next;	//ʹprָ��ͷ�ڵ��ָ����

        }

        pr->next = p;	//ʹpr��ָ����ָ���¼��ڵ�ĵ�ַ����ʱ��nextָ������ͷ�ڵ��ָ����

    }



    p->fd = fd; 			//��p��������ֵ

    sprintf(p->usrName,"%s",szName);

    sprintf(p->creatorIP,"%s",ip);

    p->isFree=1;

    p->isCreator=0;

    p->next = NULL;			//����ӵĽڵ�λ�ڱ�β����������ָ����ΪNULL

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



void DisplayNode(struct link *head) {         	//�����������ӡ����

    struct link *p = head->next;			// ����pָ��ʹ��ָ��ͷ�ڵ�

    int j = 1;									//����j��¼���ǵڼ�����ֵ

    while(p != NULL) {		//��Ϊp = p->next,����ֱ��β�ڵ��ӡ����

        printf("%5d%10d\n",j,p->fd);

        p = p->next;		//��Ϊ�ڵ��Ѿ������ɹ�������p��ָ����ͷ�ڵ�ָ����һ���ڵ�(ÿһ���ڵ��ָ����ָ������һ���ڵ�)

        j++;

    }

}



void GetAllFreeCreators(struct link *head,char *buf) {         	//�����������ӡ����

    struct link *p = head->next;			// ����pָ��ʹ��ָ��ͷ�ڵ�



    while(p != NULL)

    {

        if(p->isCreator && p->isFree)

        {

            strcat(buf,",");//���������û���֮���ö��Ÿ���

            strcat(buf,p->usrName);

            strcat(buf,"(");

            strcat(buf,p->creatorIP);

            strcat(buf,")");

        }

        p = p->next;

    }

}





void DeleteMemory(struct link *head) {			//�ͷ���Դ����

    struct link *p = head->next,*pr = NULL;	        //����pָ��ָ��ͷ�ڵ�

    while(p != NULL) {				//��p��ָ����ΪNULL

        pr = p;									//��ÿһ���ڵ�ĵ�ַ��ֵ��prָ��

        p = p->next;			        //ʹpָ����һ���ڵ�

        free(pr);								//�ͷŴ�ʱprָ��ڵ���ڴ�

    }

}

