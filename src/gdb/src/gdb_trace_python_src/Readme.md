https://www.python.org/ftp/python/3.13.0/Python-3.13.0a2.tar.xz

mkdir debug
cd debug
../configure --with-pydebug
 make
 make test


/usr/bin/gdb -q ./python
cgdb -d /usr/bin/gdb -q ./python


(gdb) rbreak tupleobject.c:.


(gdb) python
>tup1 = (1,2,3)
>end
(gdb) r
Starting program: /home/shihyu/Python-2.7.13/python
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Breakpoint 5, PyTuple_New (size=0) at Objects/tupleobject.c:53
