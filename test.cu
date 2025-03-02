#include<stdio.h>
#define CUDA_BLOCK_X 128
#define CUDA_BLOCK_Y 1
#define CUDA_BLOCK_Z 1

int ARRAY_SIZE(int *arr)
{
  return (sizeof(arr) / sizeof(arr[0]));
}

int main()
{
  int i_nom_1;
  int i;
  int vec1[3] = {(1), (2), (3)};
  int vec2[3] = {(4), (5), (6)};
  int *result;
  for (i = 1; i <= (ARRAY_SIZE(vec1) + 0) / 1; i += 1) {
    result[1 * i + -1] = 0;
  }
  for (i_nom_1 = 1; i_nom_1 <= (ARRAY_SIZE(vec1) + 0) / 1; i_nom_1 += 1) {
    result[1 * i_nom_1 + -1] = vec1[1 * i_nom_1 + -1] + vec2[1 * i_nom_1 + -1];
  }
  printf("%d \n",result[0]);
  return - 1;
}
