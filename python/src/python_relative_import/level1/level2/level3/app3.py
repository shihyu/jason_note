print('& [level1/level2/level3] app3.py')

import sys

print('__name__:', __name__)
print('__package__:', __package__)

from ...utils.tool import name

print(name)