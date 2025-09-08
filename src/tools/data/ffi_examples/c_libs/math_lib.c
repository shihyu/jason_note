#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 簡單的加法函數
int add(int a, int b) {
    return a + b;
}

// 計算階乘
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 打印訊息
void say_hello(const char* name) {
    printf("Hello, %s from C!\n", name);
}

// 計算陣列總和
int sum_array(int* arr, int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

// 字串反轉（修改原字串）
void reverse_string(char* str) {
    if (str == NULL) return;
    
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

// 計算斐波那契數
int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

// 結構體範例
typedef struct {
    int x;
    int y;
} Point;

// 計算兩點之間的曼哈頓距離
int manhattan_distance(Point p1, Point p2) {
    return abs(p1.x - p2.x) + abs(p1.y - p2.y);
}

// 創建點
Point create_point(int x, int y) {
    Point p = {x, y};
    return p;
}