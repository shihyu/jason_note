#include <iostream>

using namespace std;

class test2
{
    int function11(int i)
    {
        return function21(i) + 1;
    }
    int function21(int i)
    {
        return function61(i) + 1;
    }
    int function41(int i)
    {
        return function51(i) + 1;
    }
    int function51(int i)
    {
        return function61(i) + 1;
    }
    int function61(int i)
    {
        return 1;
    }
public:
    int function31(char c)
    {
        return function11(c) + 1 + function41(c);
    }
};

class test
{
    int function1(long l);
    int function2(int i);
    int function4(long l);
    int function5(int i);
    int function6(int i);
public:
    int function3(char c);
};

int
test::function1(long l)
{
    return test::function6(l) + 1;
}

int
test::function2(int i)
{
    return test::function1(i) + 1;
}

int
test::function4(long l)
{
    return test::function6(l) + 1;
}

int
test::function5(int i)
{
    return test::function4(i) + 1;
}
int
test::function6(int i)
{
    return i + 1;
}
int
test::function3(char c)
{
    return test::function2(c) + 1 + test::function6(c) + 1;
}

int main()
{
    class test* ptest;
    class test2* ptest2;

    ptest = new test();
    ptest2 = new test2();

    return ptest->function3(1) + ptest2->function31(1);
}

