#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
int csum(int* arr, int size){
    int  res = 0;
    for(int i=1;i<(size * 200);i+=1){
        res = (res + arr[(i % size)]);
    }
    return res;
}
