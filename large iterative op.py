

from typing import List
from mini.PUDA import to_c
import time


@to_c(dbg=True)
def csum(arr:List[int],size:int)->int:
    res:int=0
    
    for i in range(1,size*200):
        res=res+arr[i%size]
    return res
    
la=[i for i in range(1000000)] 
s=time.time()
print(csum(la,len(la)))
print(f"Time taken: {time.time()-s}")

s=time.time()
def csum(arr:List[int],size:int)->int:
    res:int=0
    
    for i in range(1,size*200):
        res=res+arr[i%size]
    return res
csum(la,len(la))
print(f"Time taken: {time.time()-s}")