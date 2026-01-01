#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_SIZE (1024 * 1024 * 100) // 100MB per chunk

int main() {
    printf("OOM Trigger started. Allocating memory...\n");
    printf("My PID: %d\n", getpid());
    
    size_t total = 0;
    while (1) {
        void *p = malloc(CHUNK_SIZE);
        if (p == NULL) {
            printf("Malloc failed! Total allocated: %zu MB\n", total / (1024 * 1024));
            // Keep going or wait to be killed
            sleep(1);
            continue;
        }
        
        // Critical: must touch the memory to actually allocate pages
        memset(p, 0, CHUNK_SIZE);
        total += CHUNK_SIZE;
        
        printf("Allocated: %zu MB\n", total / (1024 * 1024));
        usleep(100000); // 0.1s
    }
    
    return 0;
}

