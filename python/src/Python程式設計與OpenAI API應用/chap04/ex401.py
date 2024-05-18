from threading import current_thread, Thread as Thread
from time import sleep, perf_counter

def print_hello():
    sleep(2)
    print(f"{current_thread().name}: Hello")

def print_message(msg):
    sleep(1)
    print(f"{current_thread().name}: {msg}")

start = perf_counter()

# create threads
t1=Thread(target=print_hello, name="Th01")
t2=Thread(target=print_hello, name="Th02")
t3=Thread(target=print_message, args=("Good morning",), name="Th03")

# start the threads
t1.start()
t2.start()
t3.start()

# wait till all are done
t1.join()
t2.join()
t3.join()

elapsed = perf_counter() - start
print(f"elapsed: {elapsed:.2f} sec")

