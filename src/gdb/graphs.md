## gdb_graphs

https://github.com/tarun27sh/gdb_graphs

- ~/.gdbinit

```sh
set pagination off
set print pretty
set logging file ./test.log
set logging enabled on
```

- test.c

```c
#include<stdio.h>
#include<stdbool.h>
#include<stdlib.h>
#include<time.h>


static void func9(void) { printf("leaf\n"); }

void func8(void) { func9(); }

void func7_1(bool is_true, int *p) { printf("leaf (is_true=%d, ptr=%p\n", is_true, p); }
void func7(void) { func8(); }

void func6(void) { func7(); }

void func5_1(const char* str) { printf("leaf (%s)\n", str); }
void func5(void) {
    func5_1("graph me\n");
    func6();
}

void func4(void) { func5(); }
void func3_1(int a, int b, int c) { printf("leaf\n"); }
void func3(void) {
    func3_1(rand(), rand(), rand());
    func4();
}

void func2_1(int a, int b) { printf("leaf (%d, %d)\n", a, b);}
void func2(void) {
    func2_1(rand(),rand());
    func3();
}
void func1(void) { func2(); }
int main()
{
    srand(time(NULL));
    for(int i=0; i<10; ++i) {
            func1();
    }
        return 0;
}
```

```sh
gcc -g test.c -o test
gdb ./test

(gdb) rbreak test.c:.

Breakpoint 1 at 0x13a9: file test.c, line 37.
void func1(void);
Breakpoint 2 at 0x137a: file test.c, line 33.
void func2(void);
Breakpoint 3 at 0x134c: file test.c, line 32.
void func2_1(int, int);
Breakpoint 4 at 0x1316: file test.c, line 27.
void func3(void);
Breakpoint 5 at 0x12f2: file test.c, line 26.
void func3_1(int, int, int);
Breakpoint 6 at 0x12e2: file test.c, line 25.
void func4(void);
Breakpoint 7 at 0x12c6: file test.c, line 20.
void func5(void);
Breakpoint 8 at 0x129b: file test.c, line 19.
void func5_1(const char *);
Breakpoint 9 at 0x128b: file test.c, line 17.
void func6(void);
Breakpoint 10 at 0x1243: file test.c, line 11.
void func7(void);
Breakpoint 11 at 0x1210: file test.c, line 10.
void func7_1(_Bool, int *);
Breakpoint 12 at 0x1200: file test.c, line 8.
void func8(void);
Breakpoint 13 at 0x13b9: file test.c, line 39.
int main();
Breakpoint 14 at 0x11e9: file test.c, line 7.
static void func9(void);


(gdb) commands
Type commands for breakpoint(s) 1-14, one per line.
End with a line saying just "end".
>bt
>c
>end
(gdb) r


Breakpoint 1, func1 () at test.c:37
37	void func1(void) { func2(); }
#0  func1 () at test.c:37
#1  0x00005555555553e4 in main () at test.c:42

Breakpoint 2, func2 () at test.c:33
33	void func2(void) { 
#0  func2 () at test.c:33
#1  0x00005555555553b6 in func1 () at test.c:37
#2  0x00005555555553e4 in main () at test.c:42

Breakpoint 3, func2_1 (a=32767, b=-136364723) at test.c:32
32	void func2_1(int a, int b) { printf("leaf (%d, %d)\n", a, b);}
#0  func2_1 (a=32767, b=-136364723) at test.c:32
#1  0x000055555555539c in func2 () at test.c:34
#2  0x00005555555553b6 in func1 () at test.c:37
#3  0x00005555555553e4 in main () at test.c:42
leaf (1316343669, 1810645944)
...

[Inferior 1 (process 672172) exited normally]

Once the program finishes, it would have dumped the logs to the disk in `test.log` 
```



```sh
sudo apt-get install graphviz
pip install -r requiments.txt
```

- ### Run gen_graph.py

```sh
python gen_graph.py -i test/test.log 
```

```sh
03/22/2023 08:33:26 PM [1] processing gdb bt data
03/22/2023 08:33:26 PM [2] adding nodes, edges, #ofnodes=14
03/22/2023 08:33:27 PM [3] Embedding JS
03/22/2023 08:33:27 PM [4] saving graph to:
03/22/2023 08:33:27 PM       /media/shihyu/ssd1/github/jason_note/src/gdb/src/gdb_graphs/test.svg

03/22/2023 08:33:27 PM Finished
```

