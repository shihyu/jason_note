# example:
#     1. sys.path 的作用
#     2. sys.modules 的作用
#     3. import 的流程
#     4. import package 意味著什麼

print('& app1.py')

import sys
for idx, path in enumerate(sys.path):
    print(f'sys.path[{idx}]: {path}')

print('========== phase1 ==========')
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase2 ==========')
from packageA.packageB import moduleB
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase3 ==========')
from packageA import moduleA
print('"packageA" in sys.modules:', 'packageA' in sys.modules)
print('"packageA.moduleA" in sys.modules:', 'packageA.moduleA' in sys.modules)
print('"packageA.packageB" in sys.modules:', 'packageA.packageB' in sys.modules)
print('"packageA.packageB.moduleB" in sys.modules:', 'packageA.packageB.moduleB' in sys.modules)

print('========== phase4 ==========')
import packageA
print('packageA:', packageA)