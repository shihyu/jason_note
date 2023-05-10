# Python模塊-進程間的通信(Queue,Pipe)與數據共享(Manager)

出處: http://www.taroballz.com/2018/01/11/processing_communcation/

# Introduction:

- 進程之間**互相獨立**，預設為**不能共享數據**
- 透過multiprocess模塊中的Pipe及Queue實現不同進程之間的通信
  - Queue(隊列)：
    - 先進來的先出去，後進來的後出去
- 透過Manager實現進程之間的數據共享

# Notice:

- 使用queue.Queue()調用的方法為線程隊列不適用於進程間的通信

# Usage:

## Queue :

```python
from multiprocessing import Process,Queue

def func(q,name):                        #以參數的方式將對列物件以參數型式導入子進程          
    q.put('My Process_name is %s and put the data to the id %d queue'%(name,id(q)))
       
if __name__ == "__main__":
    q = Queue()              #於主進程創建隊列物件
    process_list=[]
    print("main queue id: %d"%id(q))
    for i in range(3):
        proc = Process(target=func,args=(q,'Process-%d'%i))
        process_list.append(proc)
        proc.start()
    print(q.get())    #往管道中取數據
    print(q.get())
    print(q.get())
    for each_process in process_list:
        each_process.join() 
```

- Queue()

  參數可填入管道的長度

  - `Queue(3)`表示創建能存三筆資料的管道物件

- 創建的`Queue`物件可放置任意數據類型

- 通過 Queue.get() 取數據

  - 先`put`的先取出，後`put`的後取出
  - 要是`Queue`為空的情況下，還執意`get`的話，會堵塞到有數據可取出為止
  - 可使用`Queue.get_nowait()`方法，要是**堵塞**了會直接**報錯**

其結果如下

```shell
main queue id: 52342000
My Process_name is Process-1 and put the data to the id 64566512 queue
My Process_name is Process-0 and put the data to the id 43398512 queue
My Process_name is Process-2 and put the data to the id 61551856 queue
```


從上面執行結果可知道我們所創建的Queue物件似乎為一個copy的對象並指向不同RAM地址貌似不是對同一個隊列進行操作
但是從主進程`get()`的結果卻發現的確是對同一隊列的資料進行操作，
原因應為copy後的隊列內部進行了pickle的序列化及反序列化的操作



### 判斷Queue是否為滿(full)或空(empty)

```python
Queue.full() #判斷管道是否為滿
Queue.empty() #判斷管道是否為空
```

- 返回bool值

## Pipe (類似socket通信)

```python
from multiprocessing import Process,Pipe
import os

def func(conn):
    conn.send("Hi I'm your subprocess. My ID is %d"%os.getpid())
    print("ID %d receive main_process message: "%os.getpid(),conn.recv())
    conn.close()
       
if __name__ == "__main__":
    main_conn , sub_conn = Pipe()    #使用Pipe()函數同時建立主進程及自進程兩個通信的物件
    processlist=[]
    for i in range(2):
        proc = Process(target=func,args=(sub_conn,))
        processlist.append(proc)
        proc.start()
        print("I'm mainprocess, I receive my sub_process message: ",main_conn.recv())
        main_conn.send("Remember I'm your Master")
    for each_process in processlist:
        each_process.join()
```

其結果如下

```shell
I'm mainprocess, I receive my sub_process message:  Hi I'm your subprocess. My ID is 8424
ID 8424 receive main_process message:  Remember I'm your Master
I'm mainprocess, I receive my sub_process message:  Hi I'm your subprocess. My ID is 13468
ID 13468 receive main_process message:  Remember I'm your Master
```



## Manager

```python
from multiprocessing import Process,Manager

def func(dic,lis,n):            #對字典及列表進行操作
    dic["Process_%s"%n] = "1"
    dic['2'] = 2
    dic[0.25] = None
    lis.append(n)

if __name__ == "__main__":
    with Manager() as manager:       #創建一個Manager()的物件
        dic = manager.dict()         #透過Manager()物件創建一個空字典 此字典進程之間可以共享
        lis = manager.list(range(5)) #透過Manager()物件創建一個含0-5數字的列表 此列表進程之間可以共享
        process_list = []
        for i in range(10):
            proc = Process(target=func, args=(dic,lis,i))
            proc.start()
            process_list.append(proc)
            
        for each_process in process_list:
            each_process.join()
        print(dic)
        print(lis)
```

其結果為

```shell
{0.25: None, 'Process_9': '1', '2': 2, 'Process_8': '1', 'Process_4': '1', 'Process_0': '1', 'Process_7': '1', 'Process_2': '1', 'Process_6': '1', 'Process_1': '1', 'Process_3': '1', 'Process_5': '1'}
[0, 1, 2, 3, 4, 0, 1, 2, 3, 6, 5, 4, 8, 7, 9]
```


我們可以發現使用Manager各個進程是對同一個列表及字典進行操作

# Reference:

http://www.cnblogs.com/yuanchenqi/articles/5745958.html