// cpu_intensive.cpp - 用來練習生成 CPU 火焰圖
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>

// 故意寫效率差的質數判斷（教學用）
bool is_prime_slow(int n) {
    if (n <= 1) return false;
    for (int i = 2; i < n; i++) {  // 故意不優化到 sqrt(n)
        if (n % i == 0) return false;
    }
    return true;
}

// 稍微優化的版本
bool is_prime_better(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    return true;
}

// 計算費波那契數列（遞迴版本 - 效率差）
long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

// 矩陣運算（會顯示在火焰圖中）
void matrix_multiply(std::vector<std::vector<int>>& A,
                     std::vector<std::vector<int>>& B,
                     std::vector<std::vector<int>>& C) {
    int n = A.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
            for (int k = 0; k < n; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    std::cout << "Starting CPU intensive tasks...\n";
    
    // 任務 1: 找質數（預期佔 40% CPU）
    std::cout << "Task 1: Finding primes...\n";
    int prime_count = 0;
    for (int i = 1; i <= 50000; i++) {
        if (is_prime_slow(i)) prime_count++;
    }
    std::cout << "Found " << prime_count << " primes\n";
    
    // 任務 2: 費波那契（預期佔 30% CPU）
    std::cout << "Task 2: Computing Fibonacci...\n";
    for (int i = 1; i <= 35; i++) {
        fibonacci_recursive(i);
    }
    
    // 任務 3: 矩陣運算（預期佔 30% CPU）
    std::cout << "Task 3: Matrix multiplication...\n";
    int size = 200;
    std::vector<std::vector<int>> A(size, std::vector<int>(size, 1));
    std::vector<std::vector<int>> B(size, std::vector<int>(size, 2));
    std::vector<std::vector<int>> C(size, std::vector<int>(size, 0));
    
    for (int i = 0; i < 10; i++) {
        matrix_multiply(A, B, C);
    }
    
    std::cout << "All tasks completed!\n";
    return 0;
}