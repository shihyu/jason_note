#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
int shared_counter = 0;

void* worker_thread(void* arg) {
    int thread_id = *(int*)arg;
    
    for (int i = 0; i < 5; i++) {
        pthread_mutex_lock(&mutex);
        shared_counter++;
        printf("Thread %d: Counter = %d\n", thread_id, shared_counter);
        pthread_mutex_unlock(&mutex);
        
        usleep(100000); // 0.1 second delay
    }
    return NULL;
}

int main() {
    pthread_t threads[3];
    int thread_ids[3] = {1, 2, 3};
    
    printf("Starting pthread mutex example...\n");
    
    // Create threads
    for (int i = 0; i < 3; i++) {
        if (pthread_create(&threads[i], NULL, worker_thread, &thread_ids[i]) != 0) {
            perror("pthread_create failed");
            exit(1);
        }
    }
    
    // Wait for all threads to complete
    for (int i = 0; i < 3; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Final counter value: %d\n", shared_counter);
    
    // Clean up
    pthread_mutex_destroy(&mutex);
    
    return 0;
}