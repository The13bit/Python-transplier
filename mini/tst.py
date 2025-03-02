from typing import List
def add_vectors(vec1:List[int], vec2:List[int])->List[int]:
    result:List[int] = [0,0,0]
    for i in range(len(vec1)):
        result[i] = vec1[i] + vec2[i]
    return result
    
vector1:List[int] = [1, 2, 3]
vector2:List[int] = [4, 5, 6]

print(add_vectors(vector1, vector2))
