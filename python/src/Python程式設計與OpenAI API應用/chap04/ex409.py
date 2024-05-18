import queue
import time
import threading

q = queue.Queue(5)


class Producer(threading.Thread):
    def __init__(self, thread_name):
        super().__init__()
        self.name = thread_name
        self.count = 1

    def run(self):
        while True:
            pass
            time.sleep(1)


class Consumer(threading.Thread):
    def __init__(self, thread_name):
        super().__init__()
        self.name = thread_name

    def run(self):
        while True:
            pass
            time.sleep(2)


p = Producer('producer')
p.start()

c = Consumer('consumer')
c.start()

p.join()
c.join()
