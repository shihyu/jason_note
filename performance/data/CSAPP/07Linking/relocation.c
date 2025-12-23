// 7.7 relocation
int sum(int *a, int n)
{
    int res = 0;
    for (int i = 0; i < n; ++i)
    {
        res += a[n];
    }
    return res;
}
int array[2] = {1, 2};

int main()
{
    int val = sum(array, 2);
    return val;
}