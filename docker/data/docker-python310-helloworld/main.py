from pip import _internal
import time

if __name__ == '__main__':
    _internal.main(['list'])
    while True:
        print('Hello Docker world!')
        time.sleep(1)
