// section 5.1, the limitation of compiler: memory aliasing
void p343_twiddle1(long *xp, long *yp)
{
    *xp += *yp;
    *xp += *yp;
}

void p343_twiddle2(long *xp, long *yp)
{
    *xp += 2 * *yp;
}

// section 5.1, the limitation of compiler: function call
long p343_f();
long p343_func1()
{
    return p343_f() + p343_f() + p343_f() + p343_f();
}
long p343_func2()
{
    return 4 * p343_f();
}

// section 5.6, P355, avoid unnecessary memory reference
void p355_f1(int *p, int *a, int n)
{
    for (int i = 0; i < n; ++i)
    {
        *p *= a[i];
    }
}
void p355_f2(int *p, int *a, int n)
{
    int res = *p;
    for (int i = 0; i < n; ++i)
    {
        res *= a[i];
    }
    *p = res;
}

int main(int argc, char const *argv[])
{
    return 0;
}
