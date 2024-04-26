import run_cython
import run_python
import time

# num = 1000000
num = 100

start = time.time()
print(run_python.test(num))
end = time.time()
py_time = end - start
print(f"Python time: {py_time}")


start = time.time()
print(run_cython.test(num))
end = time.time()
cy_time = end - start
print(f"Cython time: {cy_time}")
