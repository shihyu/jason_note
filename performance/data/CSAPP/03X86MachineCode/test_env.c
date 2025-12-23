// test of difference of environments
// 64 bit Windows  vs  64bit Linux
// both GCC 12.1.0

// register of parameters
void test_of_parameters(char a, short b, int c, long d,
    char* pa, short *pb, int *pc, long* pd)
{
    *pa = a;
    *pb = b;
    *pc = c;
    *pd = d;
}