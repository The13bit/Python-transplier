
from re import L
from typing import List
from mini.PUDA import to_c 
import ctypes
import random
import time

@to_c
def add()->int:
    
    return 1+2+3*34%13
    




x=add()
print(x)
