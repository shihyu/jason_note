#include <stdio.h>
#include "math_utils.h"
#include "string_utils.h"

int main() {
    // 使用數學工具
    double radius = 5.0;
    printf("Circle area: %.2f\n", calculate_area(radius));
    printf("Sphere volume: %.2f\n", calculate_volume(radius));

    // 使用字串工具
    char text[] = "hello world";
    to_uppercase(text);
    printf("Uppercase: %s\n", text);

    const char *sentence = "This is a test sentence";
    printf("Word count: %d\n", count_words(sentence));

    return 0;
}