CC=gcc
CFLAGS=-Wall -g
INCLUDES=-I /home/shihyu/github/jemalloc/include
ALLOC_DEP=/home/shihyu/github/jemalloc/lib/libjemalloc.a
ALLOC_LINK=$(ALLOC_DEP) -lpthread -ldl

dtest: dtest.o
	$(CC) $(INCLUDES) $(CFLAGS) -o dtest dtest.o $(ALLOC_LINK)

dtest.o: dtest.c $(ALLOC_DEP)
	$(CC) -c $(INCLUDES) $(CFLAGS) dtest.c

clean:
	rm -f dtest dtest.o
