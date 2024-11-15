#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <getopt.h>

#define ARRAY_SIZE (256 * 1024 * 1024)  // 256MB
#define ITERATIONS 1000000

void print_usage(const char* program)
{
    printf("Usage: %s [-m]\n", program);
    printf("Options:\n");
    printf("  -m    Enable mlockall\n");
}

int main(int argc, char* argv[])
{
    char* array;
    int use_mlockall = 0;
    int opt;

    // 解析命令行參數
    while ((opt = getopt(argc, argv, "mh")) != -1) {
        switch (opt) {
        case 'm':
            use_mlockall = 1;
            break;

        case 'h':
            print_usage(argv[0]);
            return 0;

        default:
            print_usage(argv[0]);
            return 1;
        }
    }

    // 分配記憶體
    array = (char*)malloc(ARRAY_SIZE);

    if (!array) {
        perror("malloc failed");
        return 1;
    }

    // 如果指定了 -m 參數，使用 mlockall
    if (use_mlockall) {
        if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
            perror("mlockall failed");
            free(array);
            return 1;
        }

        printf("mlockall enabled\n");
    } else {
        printf("mlockall disabled\n");
    }

    // 初始化記憶體
    memset(array, 0, ARRAY_SIZE);

    // 主要測試循環
    for (int i = 0; i < ITERATIONS; i++) {
        int index = rand() % (ARRAY_SIZE - 4096);

        // 每次讀寫 4KB (一個頁面大小)
        for (int j = 0; j < 4096; j++) {
            array[index + j] = (char)(i & 0xFF);
        }
    }

    // 清理
    if (use_mlockall) {
        munlockall();
    }

    free(array);

    return 0;
}
