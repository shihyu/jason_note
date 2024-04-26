import run_cython
import run_python
import time

# num = 1000000
num = 100000

start = time.time()
run_python.test(num)
end = time.time()
py_time = end - start
print(f"Python time: {py_time}")


start = time.time()
run_cython.test(num)
end = time.time()
cy_time = end - start
print(f"Cython time: {cy_time}")
