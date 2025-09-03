#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_spinlock_t spinlock;
int shared_data = 0;

void* fast_operation(void* arg) {
    int thread_id = *(int*)arg;
    
    for (int i = 0; i < 1000000; i++) {
        pthread_spin_lock(&spinlock);
        shared_data++;  // 很快完成的操作
        pthread_spin_unlock(&spinlock);
    }
    
    printf("Thread %d completed\n", thread_id);
    return NULL;
}

int main() {
    pthread_t threads[2];
    int thread_ids[2] = {1, 2};
    
    printf("Starting spinlock example...\n");
    
    // 初始化自旋鎖
    if (pthread_spin_init(&spinlock, PTHREAD_PROCESS_PRIVATE) != 0) {
        perror("pthread_spin_init failed");
        exit(1);
    }
    
    // 創建執行緒
    for (int i = 0; i < 2; i++) {
        if (pthread_create(&threads[i], NULL, fast_operation, &thread_ids[i]) != 0) {
            perror("pthread_create failed");
            exit(1);
        }
    }
    
    // 等待執行緒完成
    for (int i = 0; i < 2; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Final shared_data value: %d\n", shared_data);
    
    // 清理
    pthread_spin_destroy(&spinlock);
    
    return 0;
}