#include <stdio.h>
#include <stdlib.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
int main(){
    float vec1[5000];
    memset(vec1, 0, 5000 * sizeof(float));
    float vec2[5000];
    memset(vec2, 0, 5000 * sizeof(float));
    float result[ARRAYSIZE(&vec1)];
    for(int i = 0; i < ARRAYSIZE(&vec1); i++) {
        result[i] = 0;
    }
    for(int i=0;i<ARRAYSIZE(&vec1);i+=1){
        result[i] = vec1[i] + vec2[i];
    }
    printf("%f \n",result[0]);
    return -1;
}
