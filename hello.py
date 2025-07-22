from re import A, L
from typing import List
import mini
from mini.PUDA import to_c
import ctypes
import random
import time

import mini.PUDA

#@to_c(dbg=True)
def matrix_multiply(
    A: List[List[float]],
    B: List[List[float]],
    res: List[List[float]],
    rows_A: int,
    cols_A: int,
    cols_B: int,
):
    print("hello test123")

    for i in range(rows_A):
        for j in range(cols_B):
      
                res[i][j] += (A[i][j] * B[i][j])/3394
           # print(res[i][j])
    return res

random.seed(0)

A = [[random.uniform(-1, 1) for _ in range(2000)] for _ in range(2000)]
B = [[random.uniform(-1, 1) for _ in range(2000)] for _ in range(2000)]
rows_A = len(A)
cols_A = len(A[0])
cols_B = len(B[0])
result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
start=time.time()

result = matrix_multiply(A, B,result, rows_A, cols_A, cols_B)
print(f"time Taken PUDA:{time.time()-start}",result[0][0])
#print(mini.PUDA.overhead)


