from re import A, L
from typing import List
import time
import random

from mini.PUDA import to_c
@to_c(dbg=False)
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
random.seed(0)
A = [[random.uniform(-1, 1) for _ in range(512)] for _ in range(512)]
B = [[random.uniform(-1, 1) for _ in range(512)] for _ in range(512)]
rows_A = len(A)
cols_A = len(A[0])
cols_B = len(B[0])
result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
start=time.time()

result = matrix_multiply(A, B,result, rows_A, cols_A, cols_B)

print(f"time Taken PUDA:{time.time()-start}",result[0][0])

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
random.seed(0)
A = [[random.uniform(-1, 1) for _ in range(512)] for _ in range(512)]
B = [[random.uniform(-1, 1) for _ in range(512)] for _ in range(512)]
rows_A = len(A)
cols_A = len(A[0])
cols_B = len(B[0])
result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
start=time.time()

result = matrix_multiply(A, B,result, rows_A, cols_A, cols_B)

print(f"time Taken Python:{time.time()-start}",result[0][0])