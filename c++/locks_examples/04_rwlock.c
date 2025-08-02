#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;
int shared_data = 0;

void* reader(void* arg) {
    int reader_id = *(int*)arg;
    
    for (int i = 0; i < 3; i++) {
        pthread_rwlock_rdlock(&rwlock);
        printf("Reader %d: Reading data = %d\n", reader_id, shared_data);
        sleep(1); // 模擬讀取時間
        pthread_rwlock_unlock(&rwlock);
        
        usleep(500000); // 0.5 second delay
    }
    return NULL;
}

void* writer(void* arg) {
    int writer_id = *(int*)arg;
    
    for (int i = 0; i < 2; i++) {
        pthread_rwlock_wrlock(&rwlock);
        shared_data++;
        printf("Writer %d: Updated data to %d\n", writer_id, shared_data);
        sleep(1); // 模擬寫入時間
        pthread_rwlock_unlock(&rwlock);
        
        sleep(2); // 較長的延遲
    }
    return NULL;
}

int main() {
    pthread_t readers[3], writers[2];
    int reader_ids[3] = {1, 2, 3};
    int writer_ids[2] = {1, 2};
    
    printf("Starting read-write lock example...\n");
    
    // 創建讀者執行緒
    for (int i = 0; i < 3; i++) {
        if (pthread_create(&readers[i], NULL, reader, &reader_ids[i]) != 0) {
            perror("pthread_create reader failed");
            exit(1);
        }
    }
    
    // 創建寫者執行緒
    for (int i = 0; i < 2; i++) {
        if (pthread_create(&writers[i], NULL, writer, &writer_ids[i]) != 0) {
            perror("pthread_create writer failed");
            exit(1);
        }
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 3; i++) {
        pthread_join(readers[i], NULL);
    }
    for (int i = 0; i < 2; i++) {
        pthread_join(writers[i], NULL);
    }
    
    printf("Final data value: %d\n", shared_data);
    
    // 清理
    pthread_rwlock_destroy(&rwlock);
    
    return 0;
}