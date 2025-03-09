#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
void add_1d(int* a, int* b, int* c, int n){
    for(int i=0;i<n;i+=1){
        c[i] = a[i] + b[i];
    }
}
