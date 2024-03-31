## Python 中殺死執行緒的幾個方法





通常，突然終止執行緒被認為是一種糟糕的程式設計習慣。突然終止執行緒可能會使必須正確關閉的關鍵資源處於打開狀態。但是您可能希望在某個特定時間段過去或產生某個中斷後終止執行緒。

下面有6種方式殺死執行緒，其中前兩種較常用，我在原文的基礎上進行了一些修改，以覆蓋更多的情況。

- 在 python 執行緒中拋出異常
- 使用 flag / Event()
- 使用 traces 殺死執行緒
- 使用 multiprocessing module 殺死執行緒
- 通過將其設定為守護處理程序來殺死 Python 執行緒
- 使用隱藏函數 _stop()



## 0x01 在 python 執行緒中拋出異常

此方法使用函數 [PyThreadState_SetAsyncExc()](https://docs.python.org/3/c-api/init.html?highlight=pythreadstate_setasyncexc#c.PyThreadState_SetAsyncExc) 線上程中引發異常。

這種方法主要分兩步。第一步獲取執行緒id，第二步呼叫 SetAsyncExc，另外可以通過返回值查看是否殺死成功。 例如：

```
# Python program raising
# exceptions in a python
# thread

import threading
import ctypes
import time

class thread_with_exception(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
			
	def run(self):

		# target function of the thread class
		try:
			while True:
				print('running ' + self.name)
		finally:
			print('ended')
		
	def get_id(self):

		# returns id of the respective thread
		if hasattr(self, '_thread_id'):
			return self._thread_id
		for id, thread in threading._active.items():
			if thread is self:
				return id

	def raise_exception(self):
		thread_id = self.get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
			ctypes.py_object(SystemExit))
		if res > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
			print('Exception raise failure')
	
t1 = thread_with_exception('Thread 1')
t1.start()
time.sleep(2)
t1.raise_exception()
t1.join()
```

另外，[這裡](https://www.cnblogs.com/lucky-heng/p/11986091.html)還有另一種方法獲取執行緒的 id：

```
import threading
import time
import inspect
import ctypes


def _async_raise(tid, exctype):
    """Raises an exception in the threads with id tid"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class TestThread(threading.Thread):
    def run(self):
        print("begin run the child thread")
        while True:
            print("sleep 1s")
            time.sleep(1)


if __name__ == "__main__":
    print("begin run main thread")
    t = TestThread()
    t.start()
    time.sleep(3)
    stop_thread(t)
    print("main thread end")
```

當我們在一臺機器上運行上面的程式碼時，你會注意到，只要函數 raise_exception() 被呼叫，目標函數 run() 就會結束。這是因為一旦引發異常，程序控制就會跳出 try 塊，run() 函數將終止。之後可以呼叫 join() 函數來終止執行緒。在沒有函數 run_exception() 的情況下，目標函數 run() 將一直運行，並且永遠不會呼叫 join() 函數來終止執行緒。  

## 0x02 使用 flag

為了殺死一個執行緒，我們可以聲明一個停止標誌，這個標誌會被執行緒檢查。例如

```
# Python program showing
# how to kill threads
# using set/reset stop
# flag

import threading
import time

def run():
	while True:
		print('thread running')
		global stop_threads
		if stop_threads:
			break

stop_threads = False
t1 = threading.Thread(target = run)
t1.start()
time.sleep(1)
stop_threads = True
t1.join()
print('thread killed')
```

在上面的程式碼中，一旦設定了全域變數 stop_threads，目標函數 run() 就會結束，並且可以使用 t1.join() 殺死執行緒 t1。但是由於某些原因，人們可能會避免使用全域變數。對於這些情況，可以傳遞函數對象以提供類似的功能，如下所示。

```
# Python program killing
# threads using stop
# flag

import threading
import time

def run(stop):
	while True:
		print('thread running')
		if stop():
				break
				
def main():
		stop_threads = False
		t1 = threading.Thread(target = run, args =(lambda : stop_threads, ))
		t1.start()
		time.sleep(1)
		stop_threads = True
		t1.join()
		print('thread killed')
main()
```

上面程式碼中傳入的函數對象總是返回局部變數 stop_threads 的值。這個值在函數 run() 中被檢查，一旦 stop_threads 被重設，run() 函數結束並且執行緒可以被殺死。

另外，使用 `threading.Event()` 可以更優雅的實現這一功能。

## 0x03 使用 traces 殺死執行緒

此方法通過在每個執行緒中使用 **traces** 來工作。每個 trace 都會在檢測到某些刺激或標誌時自行終止，從而立即終止關聯的執行緒。例如

```
Python program using
# traces to kill threads

import sys
import trace
import threading
import time
class thread_with_trace(threading.Thread):
def __init__(self, *args, **keywords):
	threading.Thread.__init__(self, *args, **keywords)
	self.killed = False

def start(self):
	self.__run_backup = self.run
	self.run = self.__run	
	threading.Thread.start(self)

def __run(self):
	sys.settrace(self.globaltrace)
	self.__run_backup()
	self.run = self.__run_backup

def globaltrace(self, frame, event, arg):
	if event == 'call':
	return self.localtrace
	else:
	return None

def localtrace(self, frame, event, arg):
	if self.killed:
	if event == 'line':
		raise SystemExit()
	return self.localtrace

def kill(self):
	self.killed = True

def func():
while True:
	print('thread running')

t1 = thread_with_trace(target = func)
t1.start()
time.sleep(2)
t1.kill()
t1.join()
if not t1.isAlive():
print('thread killed')
```

在這段程式碼中，start() 被稍微修改為使用 [settrace()](https://docs.python.org/2/library/sys.html?highlight=settrace#sys.settrace) 設定系統跟蹤功能。本地跟蹤函數的定義是，無論何時設定相應執行緒的終止標誌（已終止），都會引發 [SystemExit](https://www.geeksforgeeks.org/built-exceptions-python/) 異常執行下一行程式碼，結束目標函數func的執行。現在可以使用 join() 終止執行緒。

## 0x04 使用 multiprocessing module 殺死執行緒

Python 的[multiprocessing module](https://www.geeksforgeeks.org/multiprocessing-python-set-1/) 允許您以類似於使用執行緒模組生成執行緒的方式生成處理程序。multiprocessing module 的介面與 threading 的介面類似。例如，在給定的程式碼中，我們建立了三個執行緒（處理程序），它們從 1 計數到 9。

```
# Python program creating
# three threads

import threading
import time

# counts from 1 to 9
def func(number):
	for i in range(1, 10):
		time.sleep(0.01)
		print('Thread ' + str(number) + ': prints ' + str(number*i))

# creates 3 threads
for i in range(0, 3):
	thread = threading.Thread(target=func, args=(i,))
	thread.start()
```

上述程式碼的功能也可以通過類似的方式使用多處理模組來實現，只需很少的改動。請參閱下面給出的程式碼。  

```
# Python program creating
# thread using multiprocessing
# module

import multiprocessing
import time

def func(number):
	for i in range(1, 10):
		time.sleep(0.01)
		print('Processing ' + str(number) + ': prints ' + str(number*i))

for i in range(0, 3):
	process = multiprocessing.Process(target=func, args=(i,))
	process.start()
```

儘管這兩個模組的介面相似，但是這兩個模組的實現卻截然不同。所有執行緒共享全域變數，而處理程序彼此完全分離。因此，與殺死執行緒相比，殺死處理程序要安全得多。 Process 類提供了一種方法 [terminate()](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process#multiprocessing.Process.terminate) 來終止處理程序。現在，回到最初的問題。假設在上面的程式碼中，我們想要在 0.03s 過去後殺死所有處理程序。此功能是使用以下程式碼中的 multiprocessing 實現的。

```
# Python program killing
# a thread using multiprocessing
# module

import multiprocessing
import time

def func(number):
	for i in range(1, 10):
		time.sleep(0.01)
		print('Processing ' + str(number) + ': prints ' + str(number*i))

# list of all processes, so that they can be killed afterwards
all_processes = []

for i in range(0, 3):
	process = multiprocessing.Process(target=func, args=(i,))
	process.start()
	all_processes.append(process)

# kill all processes after 0.03s
time.sleep(0.03)
for process in all_processes:
	process.terminate()
```

雖然這兩個模組有不同的實現。上面程式碼中多處理模組提供的這個功能類似於殺死執行緒。因此，只要我們需要在 Python 中實現執行緒終止，`multiprocessing` 就可以作為一個簡單的替代方案。

## 0x05 通過將其設定為守護處理程序（daemon）來殺死 Python 執行緒

[守護執行緒](https://docs.python.org/3/library/threading.html#threading.Thread.daemon) 是那些在主程序退出時被殺死的執行緒。例如

 

```
import threading
import time
import sys

def func():
	while True:
		time.sleep(0.5)
		print("Thread alive, and it won't die on program termination")

t1 = threading.Thread(target=func)
t1.start()
time.sleep(2)
sys.exit()
```

請注意，執行緒 t1 保持活動狀態並阻止主程序通過 sys.exit() 退出。在 Python 中，任何活動的非守護執行緒都會阻止主程序退出。然而，一旦主程序退出，守護執行緒本身就會被殺死。換句話說，主程序一退出，所有的守護執行緒就被殺死了。要將執行緒聲明為守護處理程序，我們將關鍵字參數 daemon 設定為 True。例如，在給定的程式碼中，它演示了守護執行緒的屬性。

```
# Python program killing
# thread using daemon

import threading
import time
import sys

def func():
	while True:
		time.sleep(0.5)
		print('Thread alive, but it will die on program termination')

t1 = threading.Thread(target=func)
t1.daemon = True
t1.start()
time.sleep(2)
sys.exit()
```

請注意，一旦主程序退出，執行緒 t1 就會被終止。在程序終止可用於觸發執行緒終止的情況下，此方法被證明非常有用。請注意，在 Python 中，只要所有非守護執行緒都死了，主程序就會終止，而不管有多少守護執行緒處於活動狀態。因此，這些守護執行緒所持有的資源，例如打開的檔案、資料庫事務等，可能無法正常釋放。 python 程序中的初始控制執行緒不是守護執行緒。除非確定知道這樣做不會導致任何洩漏或死鎖，否則不建議強行終止執行緒。

## 0x06 使用隱藏函數 `_stop()`

為了殺死一個執行緒，我們使用隱藏函數 `_stop()` 這個函數沒有記錄但可能會在下一版本的 python 中消失。

```
# Python program killing
# a thread using ._stop()
# function

import time
import threading

class MyThread(threading.Thread):

	# Thread class with a _stop() method.
	# The thread itself has to check
	# regularly for the stopped() condition.

	def __init__(self, *args, **kwargs):
		super(MyThread, self).__init__(*args, **kwargs)
		self._stop = threading.Event()

	# function using _stop function
	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		while True:
			if self.stopped():
				return
			print("Hello, world!")
			time.sleep(1)

t1 = MyThread()

t1.start()
time.sleep(5)
t1.stop()
t1.join()
```

**注意：** 以上方法在某些情況下可能不起作用，因為 python 沒有提供任何直接殺死執行緒的方法。
