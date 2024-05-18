def greeting():
    print('Hello')
    yield 1
    print('World')
    yield 2
    print('How are you')
    yield 3

mess = greeting()
result = next(mess)
print(f"mess_1 : {result}")
result = next(mess)
print(f"mess_2 : {result}")
result = next(mess)
print(f"mess_3 : {result}")

