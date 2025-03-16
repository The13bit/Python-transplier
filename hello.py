from re import A, L
from typing import List
import mini
from mini.PUDA import to_c
import ctypes
import random
import time

import mini.PUDA

@to_c(dbg=True)
def matrix_multiply(
    A: List[List[float]],
    B: List[List[float]],
    res: List[List[float]],
    rows_A: int,
    cols_A: int,
    cols_B: int,
):
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                res[i][j] += A[i][k] * B[k][j]
    return res


A = [[random.uniform(-1, 1) for _ in range(64)] for _ in range(512)]
B = [[random.uniform(-1, 1) for _ in range(512)] for _ in range(64)]
rows_A = len(A)
cols_A = len(A[0])
cols_B = len(B[0])
result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
start=time.time()

result = matrix_multiply(A, B,result, rows_A, cols_A, cols_B)
print(f"time Taken:{time.time()-start}",result[0][0])
print(mini.PUDA.overhead)
def matrix_multiply(
    A: List[List[float]],
    B: List[List[float]],
    res: List[List[float]],
    rows_A: int,
    cols_A: int,
    cols_B: int,
):
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                res[i][j] += A[i][k] * B[k][j]
    return res
result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
start=time.time()

result = matrix_multiply(A, B,result, rows_A, cols_A, cols_B)
print(f"time Taken:{time.time()-start}",result[0][0])