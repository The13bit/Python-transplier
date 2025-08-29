
## PUDA 

PUDA is a python to C trancompiler that allows you to write Python code and compile it to C for performance improvements. It is designed to be easy to use and integrate with existing Python codebases.

## Example
```python
from mini.PUDA import to_c
from re import A, L
from typing import List
import mini
from mini.PUDA import to_c
import ctypes
import random
import time
@to_c()
def matrix_multiply(
     #Treat Arrays as you would treat them in C
    #When a function is decorated with @ to_c all function arguments types along with return type should be specified if any.
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
```
Comparison of running the above code with and without PUDA:

|With PUDA|Without PUDA|
|:---:|:---:|
|1.7489 sec|26.9894 sec|

## Features
- Easy to use: Just decorate your Python functions with `@to_c()`.
- Each code block is cached allowing for faster reruns of the same function.
- Supports basic data types and lists.

## Limitations
- Python lists get treated as C arrays, so you need to pass additional parameters for dimensions and a result array.
- Not all Python features are supported, such as complex data structures or advanced libraries.


## Future Work
- Support for more complex data structures.
- Improve the python to C and vice versa data conversions.

## See Also
- Star this project if you find it useful! Contributions are welcome.


