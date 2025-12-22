#include <inttypes.h>
#include <stdio.h>

// Section 3.2.2, P114: example
long p114_encoding_mult2(long x, long y)
{
    return x * y;
}
void P114_encoding_multstore(long x, long y, long* dest)
{
    long t = p114_encoding_mult2(x, y);
    *dest = t;
}

// Section 3.4.3, P125: move instruction example
long P125_move_exchange(long* xp, long y)
{
    long x = *xp;
    *xp = y;
    return x;
}

// section 3.4.3, P127, exercise 3.5
void p127_exercise_3_5_decode1(long *xp, long *yp, long* zp)
{
    // xp in %rdi, yp in %rsi, zp in %rdx
    long tmp = *zp;
    *zp = *yp;
    *yp = *xp;
    *xp = tmp;
}

// section 3.5.1, P129, leaq example
long p129_leaq_scale(long x, long y, long z)
{
    // x in %rdi, y in %rsi, z in %rdx
    return x + 4*y + 12*z;
}

// section 3.5.3, P131, shift instruction, exercise 3.9
long p131_exercise_3_9_shift_left4_rightn(long x, long n)
{
    x <<= 4;
    x >>= n;
    return x;
}

// Note: GCC extension, non-standard type __int128
typedef unsigned __int128 uint128_t;
// section 3.5.5, P134, 128bit integer arithmetics
void p134_special_arith_inst_mul(uint128_t *dest, uint64_t x, uint64_t y)
{
    *dest = x * (uint128_t)y;
}

// section 3.5.5, P134, signed interger divide instruction
void P134_special_airth_inst_remdiv(long x, long y, long *qp, long *rp)
{
    // x in %rdi, y in %rsi, qp in %rdx, %rp in %rcx
    long q = x / y;
    long r = x % y;
    *qp = q;
    *rp = r;
}

// section 3.5.5, P134, unsigned interger divide instruction
void p124_sepcial_arith_inst_remdiv_unsigned(unsigned long x, unsigned long y,
    unsigned long* qp, unsigned long* rp)
{
    // x in %rdi, y in %rsi, qp in %rdx, %rp in %rcx
    unsigned long q = x / y;
    unsigned long r = x % y;
    *qp = q;
    *rp = r;
}

// section 3.6.2, P137, less than example
int p137_control_flow_less(long a, long b)
{
    return a < b;
}

// sectioon 3.6.2, P137, less than of unsigned
int p127_control_flow_less_unsinged(unsigned long a, unsigned long b)
{
    return a < b;
}

// section 3.6.4, P141, explore encoding of jump instructions
// PC relative encoding
int p141_encoding_of_jump_inst(int a)
{
    if (a > 0)
    {
        return a + 1;
    }
    return a - 1;
}

// section 3.6.5, P142, implementation of branch
long lt_cnt = 0;
long ge_cnt = 0;
long p142_absdiff_se(long x, long y)
{
    long result;
    if (x < y)
    {
        lt_cnt ++;
        result = y - x;
    }
    else
    {
        ge_cnt ++;
        result = x - y;
    }
    return result;
}

// section 3.6.5, P142, equivalent goto implementation
long p142_gotodiff_se(long x, long y)
{
    long result;
    if (x >= y)
    {
        goto x_ge_y;
    }
    lt_cnt++;
    result = y - x;
    return result;
x_ge_y:
    ge_cnt++;
    result = x - y;
    return result;
}

// section 3.6.6, P145, condtional move instructions
long p145_absdiff(long x, long y)
{
    long result;
    if (x < y)
    {
        result = y - x;
    }
    else
    {
        result = x - y;
    }
    return result;
}

// section 3.6.5, P145, conditional move
long p145_cmovdiff(long x, long y)
{
    long rval = y - x;
    long eval = x - y;
    if (x >= y)
    {
        rval = eval;
    }
    return rval;
}

// section 3.6.6, P150, factorial with do-while
long p150_factorial_dowhile(long n)
{
    long result = 1;
    do
    {
        result *= n;
        n = n-1;
    } while (n > 1);
    return result;
}

// section 3.6.6, P154, factorial with while
long p154_factorial_while(long n)
{
    long result = 1;
    while (n > 1)
    {
        result *= n;
        n--;
    }
    return result;
}

// section 3.6.6, P157, factorial with for
long p157_factorial_for(long n)
{
    long i;
    long result = 1;
    for (i = 2; i <= n; i++)
    {
        result *= n;
    }
    return result;
}

// section 3.6.7, P160, switch statement
void p160_switch_example(long x, long n, long* dest)
{
    long val = x;
    switch (n)
    {
    case 100:
        val *= 13;
        break;
    case 102:
        val += 10;
        // fall through
    case 103:
        val += 11;
        break;
    default:
        val = 0;
    }
    *dest = val;
}

// section 3.7.3, P169, passing of parameter
void p169_passing_parameter(long a1, long *a1p,
                            int a2, int *a2p,
                            short a3, short *a3p,
                            char a4, char * a4p)
{
    *a1p += a1;
    *a2p += a2;
    *a3p += a3;
    *a4p += a4;
}
void p169_passing_parameter_caller()
{
    long a = 1;
    int b = 2;
    short c = 3;
    char d = 4;
    p169_passing_parameter(1, &a, 2, &b, 3, &c, 4, &d);
}

// section 3.7.4, P170, local storage in stack
long p171_swap_add(long *xp, long *yp)
{
    long x = *xp;
    long y = *yp;
    *xp = y;
    *yp = x;
    return x + y;
}
long p171_caller()
{
    long arg1 = 534;
    long arg2 = 1057;
    long sum = p171_swap_add(&arg1, &arg2);
    long diff = arg1 - arg2;
    return sum * diff;
}

// section 3.7.5, P173, local storage in registers
long p173_Q(long x)
{
    return x;
}
long p173_P(long x, long y)
{
    long u = p173_Q(y);
    long v = p173_Q(x);
    return u + v;
}

// section 3.7.5, P174, saving of parameter registers
void p174_inner();
long p174_outter(long a, long b, long c, long d, long e, long f)
{
    p174_inner(1, 2);
    return a + b + c + d;
}

// section 3.9.1, P185, struct
struct rec
{
    int i;
    int j;
    int a[2];
    int *p;
};
void p185_test_struct(struct rec* r)
{
    r->p = &r->a[r->i + r->j];
}

// section 3.10.3, P195, memory access out of bounds and buffer overflow
void p195_do_something(char* buf);
void p195_buffer_overflow()
{
    char buf[8];
    p195_do_something(buf);
}

// section 3.11.1, P206, floating point moving instruction
float p206_floating_point_moving(float v1, float *src, float *dest)
{
    float v2 = *src;
    *dest = v1;
    return v2;
}

// section 3.11.1, P207, conversion between floating point and integer
void p207_floating_integer_conversion(int a, long b, float *fp, double *dp, int *ip, long *lp)
{
    *fp = a; // int to float
    *fp = b; // long to float
    *dp = a; // int to double
    *dp = b; // long to double
    *ip = *fp; // float to int
    *lp = *fp; // float to long
    *ip = *dp; // double to int
    *lp = *dp; // double to long
}

// section 3.11.1, P207, conversion between floating point numbers(float and double)
double p207_float_double_conversion(float *fp, double *dp)
{
    *fp = *dp;
    *dp = *fp;
    return *dp;
}

// section 3.11.2, P210, passing floating point parameters
void p210_passing_floating_parameters(float a, double b, float c, long d, double *p,
    float e, double f, float g, double h, double i, double j, double k);
void p210_passing_floating_caller()
{
    p210_passing_floating_parameters(1.0f, 2.0, 3.1f, 10L, 0,
        4.2f, 5.3, 6.4f, 7.5, 8.6, 9.7, 10.8);
}

// section 3.11.3, P210, floating point arithmetics
double p210_floating_point_airthmetics(double a, float x, double b, int i)
{
    return a*x - b/i;
}

// section 3.11.4, P212, floating point constants
double p210_floating_point_constant(double temp)
{
    return 1.8 * temp + 32.1;
}

// section 3.11.6, P214, floating point comparison
int p214_floating_point_comparison(double x)
{
    int result;
    if (x > 0)
    {
        result = 0;
    }
    else if (x == 0)
    {
        result = 1;
    }
    else if (x < 0)
    {
        result = 2;
    }
    else
    {
        result = 3;
    }
    return result;
}

int main()
{
    return 0;
}
