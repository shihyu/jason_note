// 7.5 symbol table, P468
int* p1468_f()
{
    static int x = 0;
    return &x;
}
int* p468_g()
{
    static int x = 0;
    return &x;
}
int x;