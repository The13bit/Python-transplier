#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
float c_std(int* arr, int size){
    float  mean_val = 0.0;
    for(int i=0;i<size;i+=1){
        mean_val += arr[i];
    }
    mean_val /= size;
    float  var = 0.0;
    for(int i=0;i<size;i+=1){
        float  diff = (arr[i] - mean_val);
        var += (diff * diff);
    }
    var /= size;
    return var;
}
