# example:
#     1. 實際觀察 import 與 sys.modules 的關係

print('& app4_1.py')

import sys

print('[in app4_1.py] "app4_1" in sys.modules:', 'app4_1' in sys.modules)
print('[in app4_1.py] "app4_2" in sys.modules:', 'app4_2' in sys.modules)

import app4_2

print('[in app4_1.py] "app4_1" in sys.modules:', 'app4_1' in sys.modules)
print('[in app4_1.py] "app4_2" in sys.modules:', 'app4_2' in sys.modules)
