#ifndef ALGORITHMS_H
#define ALGORITHMS_H

#ifdef __cplusplus
extern "C" {
#endif

// 排序演算法
void bubble_sort(int* arr, int n);
void quick_sort(int* arr, int low, int high);
void merge_sort(int* arr, int n);

// 搜尋演算法
int linear_search(const int* arr, int n, int target);
int binary_search(const int* arr, int n, int target);

// 數學函式
int fibonacci(int n);
int factorial(int n);
int gcd(int a, int b);

#ifdef __cplusplus
}
#endif

#endif // ALGORITHMS_H