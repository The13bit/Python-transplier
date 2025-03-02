
int ARRAY_SIZE(int* arr){
    return sizeof(arr)/sizeof(arr[0]);
}
int main(){
int vec1[3] = {1,2,3};
int vec2[3] = {4,5,6};
    int* result;
    for(int i = 0; i < ARRAY_SIZE(vec1); i++) {
        result[i] = 0;
    }
    for(int i=0;i<ARRAY_SIZE(vec1);i+=1){
        result[i] = vec1[i] + vec2[i];
    }
    printf("%d \n",result[0]);
    return -1;
}