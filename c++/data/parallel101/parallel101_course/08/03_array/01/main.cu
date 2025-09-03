#include <cstdio>
#include <cuda_runtime.h>
#include "helper_cuda.h"

__global__ void kernel(int *arr, int n) {
    for (int i = 0; i < n; i++) {
        arr[i] = i;
    }
}

int main() {
    int n = 32;
    int *arr;
    checkCudaErrors(cudaMallocManaged(&arr, n * sizeof(int)));
    kernel<<<1, 1>>>(arr, n);
    checkCudaErrors(cudaDeviceSynchronize());
    for (int i = 0; i < n; i++) {
        printf("arr[%d]: %d\n", i, arr[i]);
    }
    cudaFree(arr);
    return 0;
}
