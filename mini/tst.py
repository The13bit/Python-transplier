from typing import List




def main()->int:
    vec1:List[List[float]] = [[2.0,3.0,6.0],[2.2,32.3,4.5]]
    vec2:List[List[float]] = [[2.0,3.0,6.0],[2.2,32.3,4.5]]
    result:List[List[float]] = [[0,0,0],[0,0,0]]
    if True and 12:
        print(12)
    #start=time.time()
    #print(start)
    for i in range(len(vec1)*100000000):
             result[0][0]=((vec1[0][0]+vec2[0][0])+result[0][0])%3000
    
    #print(time.time()-start)

    print(result[0][0])
    return -1

