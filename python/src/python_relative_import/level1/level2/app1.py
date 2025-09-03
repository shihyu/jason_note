print('& [level1/level2] app1.py')

print('__name__:', __name__)
print('__package__:', __package__)

import sys
sys.path.append('../..')
sys.path = sys.path[1:]

from utils.tool import name
print(name)