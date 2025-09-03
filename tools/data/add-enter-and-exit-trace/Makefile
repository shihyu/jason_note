CC = gcc
CFLAGS = -g -no-pie -finstrument-functions

all: libfunc_trace.so example

libfunc_trace.so: func_trace.c
	$(CC) -D_LINUX_TRACE -fPIC -shared -o $@ $<

example: example.c
	$(CC) $(CFLAGS) -o $@ $< 

run: libfunc_trace.so example
	LD_PRELOAD=./libfunc_trace.so ./example

clean:
	rm -f libfunc_trace.so example

