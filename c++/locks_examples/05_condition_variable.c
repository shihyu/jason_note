#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t condition = PTHREAD_COND_INITIALIZER;
int ready = 0;
int data = 0;

void* waiter(void* arg) {
    int waiter_id = *(int*)arg;
    
    pthread_mutex_lock(&mutex);
    printf("Waiter %d: Waiting for condition...\n", waiter_id);
    
    while (!ready) {
        pthread_cond_wait(&condition, &mutex);
    }
    
    printf("Waiter %d: Condition met! Data = %d\n", waiter_id, data);
    pthread_mutex_unlock(&mutex);
    
    return NULL;
}

void* signaler(void* arg) {
    printf("Signaler: Working for 2 seconds...\n");
    sleep(2);
    
    pthread_mutex_lock(&mutex);
    data = 42;
    ready = 1;
    printf("Signaler: Setting condition and notifying waiters\n");
    pthread_cond_broadcast(&condition);  // 通知所有等待者
    pthread_mutex_unlock(&mutex);
    
    return NULL;
}

int main() {
    pthread_t waiters[3], signaler_thread;
    int waiter_ids[3] = {1, 2, 3};
    
    printf("Starting condition variable example...\n");
    
    // 創建等待者執行緒
    for (int i = 0; i < 3; i++) {
        if (pthread_create(&waiters[i], NULL, waiter, &waiter_ids[i]) != 0) {
            perror("pthread_create waiter failed");
            exit(1);
        }
    }
    
    // 讓等待者先開始等待
    sleep(1);
    
    // 創建信號者執行緒
    if (pthread_create(&signaler_thread, NULL, signaler, NULL) != 0) {
        perror("pthread_create signaler failed");
        exit(1);
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 3; i++) {
        pthread_join(waiters[i], NULL);
    }
    pthread_join(signaler_thread, NULL);
    
    printf("All threads completed\n");
    
    // 清理
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&condition);
    
    return 0;
}