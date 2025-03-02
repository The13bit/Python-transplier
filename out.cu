#include <stdio.h>
#include <string.h>
#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])
#define CUDA_BLOCK_X 128
#define CUDA_BLOCK_Y 1
#define CUDA_BLOCK_Z 1

int main()
{
  int i;
  float vec1[5000];
  memset(vec1,0,5000 * sizeof(float ));
  float vec2[5000];
  memset(vec2,0,5000 * sizeof(float ));
  ARRAY_SIZE(vec1);
  float result[ARRAY_SIZE(vec1)];
  for (i = 1; i <= (ARRAY_SIZE(vec1) + 0) / 1; i += 1) {
    result[1 * i + -1] = 0;
  }
  return - 1;
}
