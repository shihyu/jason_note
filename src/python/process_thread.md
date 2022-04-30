##  Multi-processing 和Multi-threading 的優缺點：

- Multi-processing (多處理程序/多進程)：
  1. 資料在彼此間傳遞變得更加複雜及花時間，因為一個 process 在作業系統的管理下是無法去存取別的 process 的 memory
  2. 適合需要 CPU 密集，像是迴圈計算
- Multi-threading (多執行緒/多線程)：
  1. 資料彼此傳遞簡單，因為多執行緒的 memory 之間是共用的，但也因此要避免會有 Race Condition 問題
  2. 適合需要 I/O 密集，像是爬蟲需要時間等待 request 回覆



```python
import threading, logging, time
import multiprocessing


class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            print("Producer is working...")
            time.sleep(1)


class Consumer(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            print("Consumer is working...")
            time.sleep(1)


def main():
    tasks = [Producer(), Consumer()]

    for t in tasks:
        t.start()

    time.sleep(3600)

    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s",
        level=logging.INFO,
    )
    main()

```

