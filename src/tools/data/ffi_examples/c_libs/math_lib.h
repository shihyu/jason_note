#ifndef MATH_LIB_H
#define MATH_LIB_H

// 基本數學運算
int add(int a, int b);
int factorial(int n);
int fibonacci(int n);

// 字串操作
void say_hello(const char* name);
void reverse_string(char* str);

// 陣列操作
int sum_array(int* arr, int size);

// 結構體定義
typedef struct {
    int x;
    int y;
} Point;

// 結構體相關函數
Point create_point(int x, int y);
int manhattan_distance(Point p1, Point p2);

#endif // MATH_LIB_H