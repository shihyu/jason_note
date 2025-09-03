from time import perf_counter

def task1():
    result = 0
    for i in range(10**8):
        result += 1
    return result

def task2():
    result = 0
    for i in range(10**8):
        result += 2
    return result


start = perf_counter()

result1=task1()
result2=task2()
result3=result1 + result2
print(f"result3= {result3}")

elapsed = perf_counter() - start
print(f"elapsed: {elapsed:.2f} sec")