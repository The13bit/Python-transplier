
from re import L
from typing import List
from mini.PUDA import to_c 
import ctypes
import random
@to_c
def add(a:List[List[int]],b:List[List[int]],c:List[List[int]],rows:int,cols:int)->None:
    for i in range(rows):
        for j in range(cols):
            c[i][j]=a[i][j]+b[i][j]
            print(c[i][j])



a=[[1 for _ in range(5)] for i in range(5)]
b=[[2 for _ in range(5)] for i in range(5)]
c=[[0 for i in range(5)]for i in range(5)]
n=len(a)
x,y=add(a,b,c,5,5)
print(y[-1])

@to_c
def add_1d(a:List[int],b:List[int],c:List[int],n:int)->None:
    for i in range(n):
        c[i]=a[i]+b[i]

a=[1 for _ in range(5)]
b=[2 for _ in range(5)]
c=[0 for i in range(5)]
n=len(a)
x,y=add_1d(a,b,c,5)
print(y[-1])



# lib=ctypes.CDLL("./mini/compiled_fns/compiled/406dcbce79ed4d877a0ca97239bae127.so")
# lib.add.restype=ctypes.c_int
# lib.add.argtypes=[ctypes.c_int,ctypes.c_int]
# print(lib.add(1,2))