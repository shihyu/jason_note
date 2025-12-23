.PHONY: run

run : main
	./main
main : main.c plugin.so
	gcc main.c -o main -ldl -rdynamic
plugin.so : plugin.c
	gcc -shared -fpic -o plugin.so plugin.c
clean:
	rm main plugin.so