#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

sem_t semaphore;

void* worker(void* arg) {
    int worker_id = *(int*)arg;
    
    printf("Worker %d: Waiting for resource...\n", worker_id);
    sem_wait(&semaphore);  // 取得資源
    
    printf("Worker %d: Got resource, working...\n", worker_id);
    sleep(2);  // 模擬工作
    
    printf("Worker %d: Releasing resource\n", worker_id);
    sem_post(&semaphore);  // 釋放資源
    
    return NULL;
}

int main() {
    pthread_t threads[5];
    int worker_ids[5] = {1, 2, 3, 4, 5};
    
    printf("Starting semaphore example (max 3 concurrent workers)...\n");
    
    // 初始化信號量，最多3個執行緒同時工作
    if (sem_init(&semaphore, 0, 3) != 0) {
        perror("sem_init failed");
        exit(1);
    }
    
    // 創建5個工作執行緒
    for (int i = 0; i < 5; i++) {
        if (pthread_create(&threads[i], NULL, worker, &worker_ids[i]) != 0) {
            perror("pthread_create failed");
            exit(1);
        }
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("All workers completed\n");
    
    // 清理
    sem_destroy(&semaphore);
    
    return 0;
}