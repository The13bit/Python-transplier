from typing import List



def main()->int:
    vec1:List[float] = [8.36]*5000
    vec2:List[float] = [4.97]*5000
    result:List[float] = [0]*len(vec1)
    
    for i in range(len(vec1)):
        result[i] = vec1[i] + vec2[i]

    print(result[0])
    return -1
