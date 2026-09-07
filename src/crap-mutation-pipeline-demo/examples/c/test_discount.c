#include <assert.h>
#include <stdio.h>
#include "discount.h"

int main(void) {
    assert(calculate_discount(100, 1) == 80);
    assert(calculate_discount(100, 0) == 100);
    assert(calculate_discount(-1, 1) == -1);
    printf("all tests passed\n");
    return 0;
}
