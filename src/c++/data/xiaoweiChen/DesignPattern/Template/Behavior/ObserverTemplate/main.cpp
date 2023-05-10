#include "Subject.hpp"
#include <functional>
#include <iostream>

using std::cout;
using std::endl;

//CatObserver �ӿ� è�Ĺ۲���
class CatObserver {
public:
    //è���¼�
    virtual void onMiaow() = 0;
public:
    virtual ~CatObserver() {}
};

//Tom �̳���Subjectģ���࣬ģ�����ΪCatObserver������Tom��ӵ���˶��ġ������Ĺ��ܡ�
class Tom : public Subject<CatObserver>
{
public:
    void miaoW()
    {
        cout << "��!" << endl;
        //����"è��"��
        //����ȡCatObserver��ĳ�Ա����ָ��onMiaow������Ա����ָ�����ʱ��Ҫ����һ�������thisָ����еġ�
        //������std::bind �� std::placeholders::_1����һ������ ��Ϊ ����������ʱ�ĵ�һ��������Ҳ����ǰ��Subject::publish�е�obs
        publish(std::bind(&CatObserver::onMiaow, std::placeholders::_1));
    }
};
//Jerry �̳��� CatObserver
class Jerry: public CatObserver
{
public:
    //��д��è���¼���
    void onMiaow() override
    {
        //���� ��è�С�ʱ ���� ����
        RunAway();
    }
    void RunAway()
    {
        cout << "��ֻè�����ˣ����" << endl;
    }
};
int main(int argc, char *argv[])
{
    Tom tom;
    Jerry jerry;

    //��jerryȥ����Tom�� è���¼�
    tom.subscibe(&jerry);

    tom.miaoW();
    return 0;
}