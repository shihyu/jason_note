# example:
#     1. circle import 到底會不會報錯

print('& app5_1.py')

firstName = 'peter'

print('[in app5_1.py] before import app5_2.py')

# (A) OK
import app5_2

# (B) AttributeError: partially initialized module 'app5_2' has no attribute 'lastName' (most likely due to a circular import)
# import app5_2
# print('[in app5_1.py] name:', firstName, app5_2.lastName)

# (C) ImportError: cannot import name 'lastName' from partially initialized module 'app5_2' (most likely due to a circular import)
# from app5_2 import lastName
# print('[in app5_1.py] name:', firstName, lastName)

