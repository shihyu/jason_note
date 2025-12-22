.PHONY : run

run : main
	LD_PRELOAD="./mymalloc.so" ./main
main : main.c mymalloc.so
	gcc -o main main.c
mymalloc.so : mymalloc.c
	gcc -DRUNTIME -shared -fpic -o mymalloc.so mymalloc.c -ldl

clean:
	rm main mymalloc.so