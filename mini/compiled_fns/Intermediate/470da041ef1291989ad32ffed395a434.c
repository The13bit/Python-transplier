#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
void add(int* a, int* b, int* c, int size){
    int  tmp = ARRAYSIZE(a);
    printf("%d \n",tmp);
    for(int i=0;i<size;i+=1){
        c[i] = a[i] + b[i];
        printf("%d \n",c[i]);
    }
}
