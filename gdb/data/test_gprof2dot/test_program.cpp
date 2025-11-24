#include <iostream>
#include <cmath>

class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }

    int multiply(int a, int b) {
        return a * b;
    }
};

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

void process_data() {
    Calculator calc;
    int result = calc.add(5, 3);
    std::cout << "Add result: " << result << std::endl;

    result = calc.multiply(4, 7);
    std::cout << "Multiply result: " << result << std::endl;
}

int main() {
    std::cout << "Program started" << std::endl;

    process_data();

    int fib = fibonacci(5);
    std::cout << "Fibonacci(5) = " << fib << std::endl;

    return 0;
}