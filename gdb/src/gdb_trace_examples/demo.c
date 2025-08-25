#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
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
    
    printf("Input: a = %d, b = %d\n", a, b);
    
    int result = calculate(a, b);
    
    printf("Result: %d\n", result);
    printf("Calculation: (%d + %d) + (%d * %d) = %d\n", 
           a, b, a, b, result);
    
    return 0;
}