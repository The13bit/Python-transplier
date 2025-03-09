#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
int main(){
float vec1[][3] = {{2.0,3.0,6.0},{2.2,32.3,4.5}};
float vec2[][3] = {{2.0,3.0,6.0},{2.2,32.3,4.5}};
float result[][3] = {{0,0,0},{0,0,0}};
if((true && 12)){
        printf("%d \n",12);
    }
    for(int i=0;i<ARRAYSIZE(vec1) * 100000000;i+=1){
        result[0][0] = vec1[0][0] + vec2[0][0] + result[0][0] % 3000;
    }
    printf("%f \n",result[0][0]);
    return -1;
}
