// demo.c - 用於展示 GDB 追蹤的範例程式
#include <stdio.h>

int add(int a, int b) {
    printf("Adding %d + %d\n", a, b);
    return a + b;
}

int multiply(int a, int b) {
    printf("Multiplying %d * %d\n", a, b);
    return a * b;
}

int calculate(int x, int y) {
    int sum = add(x, y);
    int product = multiply(x, y);
    int result = add(sum, product);
    return result;
}

int main() {
    int a = 5;
    int b = 3;
    
    printf("Starting calculation with a=%d, b=%d\n", a, b);
    
    int result = calculate(a, b);
    
    printf("Final result: %d\n", result);
    
    // 迴圈範例
    for(int i = 0; i < 3; i++) {
        printf("Loop iteration %d\n", i);
        result = add(result, i);
    }
    
    printf("After loop result: %d\n", result);
    
    return 0;
}
