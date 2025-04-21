import random
import time
import statistics
from mini.PUDA import to_c
from typing import List  # add List import
import numpy as np
DATA_SIZE = 1000000

# Generate random dataset of integers [0,100]
data = np.random.randint(0, 100, DATA_SIZE)
data = data.tolist()

# Pure Python benchmark
start_py = time.time()
py_mean = statistics.mean(data)
py_variance = statistics.pvariance(data)
py_std = statistics.pstdev(data)
py_time = time.time() - start_py

# PUDA-decorated functions
@to_c(dbg=True)
def c_mean(arr: List[int], size: int) -> float:
    total:float = 0.0
    for i in range(size):
        total += arr[i]
    return total / size

@to_c(dbg=True)
def c_variance(arr: List[int], size: int) -> float:
    mean_val:float = 0.0
    for i in range(size):
        mean_val += arr[i]
    mean_val /= size
    var:float = 0.0
    for i in range(size):
        diff:float = arr[i] - mean_val
        var += diff * diff
    return var / size

@to_c(dbg=True)
def c_std(arr: List[int], size: int) -> float:
    mean_val:float = 0.0
    for i in range(size):
        mean_val += arr[i]
    mean_val /= size
    var:float = 0.0
    for i in range(size):
        diff:float = arr[i] - mean_val
        var += diff * diff
    var /= size

    return var
import math

# PUDA benchmark
start_pu = time.time()
cu_mean = c_mean(data, DATA_SIZE)
cu_variance = c_variance(data, DATA_SIZE)
cu_std = c_std(data, DATA_SIZE)
c_time = time.time() - start_pu

# Print results
print(f"Python implementation time: {py_time:.4f}s")
print(f"Python - mean: {py_mean},  variance: {py_variance}, std: {py_std}")
print(f"PUDA implementation time: {c_time:.4f}s")
print(f"PUDA - mean: {cu_mean}, variance: {cu_variance}, std: {math.sqrt(cu_std)}")