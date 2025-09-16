#include <stdio.h>
#include <string.h>

// Global variables for testing nm
int global_initialized = 42;
int global_uninitialized;

// Static function
static void static_function() {
    printf("This is a static function\n");
}

// Normal function
void public_function() {
    printf("This is a public function\n");
}

// Weak symbol
__attribute__((weak)) void weak_function() {
    printf("This is a weak function\n");
}

// External weak reference (may not exist)
extern void external_weak() __attribute__((weak));

// Main function
int main() {
    const char *message = "Hello, Binary Analysis!";
    char buffer[100];

    strcpy(buffer, message);
    printf("%s\n", buffer);

    static_function();
    public_function();

    weak_function();

    // Check external weak reference
    if (external_weak) {
        external_weak();
    } else {
        printf("external_weak not available\n");
    }

    return 0;
}