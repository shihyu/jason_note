#define _GNU_SOURCE         // 必須在所有 include 之前定義
#include <stdio.h>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>
#include <stdlib.h>

// 定義線程參數結構體
typedef struct {
    int cpu_id;
    volatile int should_continue;  // 控制線程運行的標誌
} ThreadArg;

void* busy_work(void* arg)
{
    ThreadArg* thread_arg = (ThreadArg*)arg;

    // 設置 CPU 親和力
    cpu_set_t cpuset;
    CPU_ZERO( & cpuset);
    CPU_SET(thread_arg->cpu_id, & cpuset);

    pthread_t thread = pthread_self();

    if (pthread_setaffinity_np(thread, sizeof(cpu_set_t), & cpuset) != 0) {
        perror("pthread_setaffinity_np");
        return NULL;
    }

    printf("Thread started on CPU %d\n", thread_arg->cpu_id);

    // 模擬 CPU 密集型任務
    double result = 0.0;

    while (thread_arg->should_continue) {
        for (int i = 0; i < 1000000; i++) {
            result += i * 0.000001;
        }
    }

    printf("Thread on CPU %d finishing\n", thread_arg->cpu_id);
    return NULL;
}

int main()
{
    const int NUM_THREADS = 4;
    pthread_t threads[NUM_THREADS];
    ThreadArg* thread_args = malloc(NUM_THREADS* sizeof(ThreadArg));

    if (thread_args == NULL) {
        perror("Failed to allocate memory");
        return 1;
    }

    // 創建線程
    for (int i = 0; i < NUM_THREADS; i++) {
        thread_args[i].cpu_id = i;
        thread_args[i].should_continue = 1;

        if (pthread_create( & threads[i], NULL, busy_work, & thread_args[i]) != 0) {
            perror("Failed to create thread");
            free(thread_args);
            return 1;
        }
    }

    // 運行一段時間後停止
    printf("Running stress test for 10 seconds...\n");
    sleep(10);

    // 通知所有線程停止
    for (int i = 0; i < NUM_THREADS; i++) {
        thread_args[i].should_continue = 0;
    }

    // 等待所有線程結束
    for (int i = 0; i < NUM_THREADS; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            perror("Failed to join thread");
        }
    }

    // 清理資源
    free(thread_args);
    printf("Stress test completed\n");

    return 0;
}
