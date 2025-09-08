#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstring>

extern "C" {
    #include "math_lib.h"
}

// C++ 類別
class Calculator {
private:
    std::string name;
    std::vector<int> history;
    
public:
    Calculator(const char* calc_name = "Default") : name(calc_name) {}
    
    // 基本運算
    int multiply(int a, int b) {
        int result = a * b;
        history.push_back(result);
        return result;
    }
    
    int divide(int a, int b) {
        if (b == 0) {
            std::cerr << "Error: Division by zero!" << std::endl;
            return 0;
        }
        int result = a / b;
        history.push_back(result);
        return result;
    }
    
    // 使用 C 函數的複合運算
    int add_and_factorial(int a, int b) {
        int sum = add(a, b);  // 調用 C 函數
        return factorial(sum); // 調用 C 函數
    }
    
    // 計算冪次方
    int power(int base, int exp) {
        int result = 1;
        for (int i = 0; i < exp; i++) {
            result *= base;
        }
        history.push_back(result);
        return result;
    }
    
    // 獲取歷史記錄
    int get_history_size() const {
        return static_cast<int>(history.size());
    }
    
    int get_history_item(int index) const {
        if (index >= 0 && index < static_cast<int>(history.size())) {
            return history[index];
        }
        return 0;
    }
    
    // 清除歷史記錄
    void clear_history() {
        history.clear();
    }
    
    // 計算歷史記錄總和
    int sum_history() const {
        int sum = 0;
        for (int val : history) {
            sum += val;
        }
        return sum;
    }
};

// 字串處理類別
class StringProcessor {
public:
    // 轉換為大寫
    static std::string to_upper(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }
    
    // 轉換為小寫
    static std::string to_lower(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        return result;
    }
    
    // 重複字串
    static std::string repeat(const std::string& str, int times) {
        std::string result;
        for (int i = 0; i < times; i++) {
            result += str;
        }
        return result;
    }
};

// 導出 C 介面供其他語言使用
extern "C" {
    
    // Calculator 相關函數
    Calculator* Calculator_new(const char* name) { 
        return new Calculator(name); 
    }
    
    void Calculator_delete(Calculator* calc) { 
        delete calc; 
    }
    
    int Calculator_multiply(Calculator* calc, int a, int b) {
        return calc->multiply(a, b);
    }
    
    int Calculator_divide(Calculator* calc, int a, int b) {
        return calc->divide(a, b);
    }
    
    int Calculator_add_and_factorial(Calculator* calc, int a, int b) {
        return calc->add_and_factorial(a, b);
    }
    
    int Calculator_power(Calculator* calc, int base, int exp) {
        return calc->power(base, exp);
    }
    
    int Calculator_get_history_size(Calculator* calc) {
        return calc->get_history_size();
    }
    
    int Calculator_get_history_item(Calculator* calc, int index) {
        return calc->get_history_item(index);
    }
    
    void Calculator_clear_history(Calculator* calc) {
        calc->clear_history();
    }
    
    int Calculator_sum_history(Calculator* calc) {
        return calc->sum_history();
    }
    
    // 字串處理函數
    char* cpp_to_upper(const char* str) {
        if (!str) return nullptr;
        
        std::string result = StringProcessor::to_upper(str);
        char* c_str = new char[result.length() + 1];
        std::strcpy(c_str, result.c_str());
        return c_str;
    }
    
    char* cpp_to_lower(const char* str) {
        if (!str) return nullptr;
        
        std::string result = StringProcessor::to_lower(str);
        char* c_str = new char[result.length() + 1];
        std::strcpy(c_str, result.c_str());
        return c_str;
    }
    
    char* cpp_repeat_string(const char* str, int times) {
        if (!str || times <= 0) return nullptr;
        
        std::string result = StringProcessor::repeat(str, times);
        char* c_str = new char[result.length() + 1];
        std::strcpy(c_str, result.c_str());
        return c_str;
    }
    
    void cpp_free_string(char* str) {
        delete[] str;
    }
    
    // 混合使用 C 和 C++ 功能
    int cpp_fibonacci_sum(int n) {
        // 使用 C 的 fibonacci 函數計算每個斐波那契數
        // 然後用 C++ 計算總和
        int sum = 0;
        for (int i = 0; i <= n; i++) {
            sum += fibonacci(i);  // 調用 C 函數
        }
        return sum;
    }
    
    // 高階數學運算
    double cpp_calculate_distance(double x1, double y1, double x2, double y2) {
        double dx = x2 - x1;
        double dy = y2 - y1;
        return std::sqrt(dx * dx + dy * dy);
    }
    
    // 陣列處理
    int* cpp_sort_array(int* arr, int size) {
        if (!arr || size <= 0) return nullptr;
        
        std::vector<int> vec(arr, arr + size);
        std::sort(vec.begin(), vec.end());
        
        int* sorted = new int[size];
        std::copy(vec.begin(), vec.end(), sorted);
        return sorted;
    }
    
    void cpp_free_array(int* arr) {
        delete[] arr;
    }
}