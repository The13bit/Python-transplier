#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
void add(int** a, int** b, int** c, int rows, int cols){
    for(int i=0;i<rows;i+=1){
        for(int j=0;j<cols;j+=1){
            c[i][j] = a[i][j] + b[i][j];
            printf("%d \n",c[i][j]);
        }
    }
}
