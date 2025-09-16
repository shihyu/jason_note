#include "string_utils.h"
#include <string.h>
#include <ctype.h>

void to_uppercase(char *str) {
    while (*str) {
        *str = toupper(*str);
        str++;
    }
}

int count_words(const char *str) {
    int count = 0;
    int in_word = 0;

    while (*str) {
        if (isspace(*str)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
        str++;
    }
    return count;
}