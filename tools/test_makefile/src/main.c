#include <stdio.h>
#include "mylib.h"

int main() {
    printf("=== Testing Library Functions ===\n");
    hello_from_lib("User");

    int result = add_numbers(10, 20);
    printf("10 + 20 = %d\n", result);

    return 0;
}
