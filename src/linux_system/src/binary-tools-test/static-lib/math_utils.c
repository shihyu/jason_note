#include "math_utils.h"
#include <math.h>

double calculate_area(double radius) {
    return M_PI * radius * radius;
}

double calculate_volume(double radius) {
    return (4.0/3.0) * M_PI * radius * radius * radius;
}