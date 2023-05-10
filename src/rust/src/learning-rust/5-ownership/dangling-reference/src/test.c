#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define ALLOC_SIZE (1024)

void main() {
	char *buf = malloc(ALLOC_SIZE);
	char *p1 = buf;
	char *p2 = buf;

	printf("before free, p1 = 0x%x, p2 = 0x%x\n", *p1, *p2);

	free(p1);

	*p2 = 1;

//	memset(p2, 0xff, ALLOC_SIZE);

	printf("after free, p1 = 0x%x, p2 = 0x%x\n", *p1, *p2);
}


