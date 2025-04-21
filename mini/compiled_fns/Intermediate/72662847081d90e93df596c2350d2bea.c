#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
float c_mean(int* arr, int size){
    float  total = 0.0;
    for(int i=0;i<size;i+=1){
        total += arr[i];
    }
    return (total / size);
}
