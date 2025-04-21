#include <stdio.h>
#include <stdlib.h>
#include<stdbool.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
void matrix_multiply(float** A, float** B, float** res, int rows_A, int cols_A, int cols_B){
    for(int i=0;i<rows_A;i+=1){
        for(int j=0;j<cols_B;j+=1){
            for(int k=0;k<cols_A;k+=1){
                res[i][j] += (A[i][k] * B[k][j]);
            }
        }
        printf("%f \n",res[i][j]);
    }
    return res;
}
