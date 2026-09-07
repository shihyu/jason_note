#include "discount.h"

double calculate_discount(double price, int is_member) {
    if (price < 0) {
        return -1;
    }
    if (is_member) {
        return price * 0.8;
    }
    return price;
}
