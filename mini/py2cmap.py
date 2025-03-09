py_2_c_map={
    "int":"int",
    "float":"float",
    "str":"char*",
    "bool":"bool",
    "None":"void",
    "True":"true",
    "False":"false",
    "void":"void"
    
}

type_to_printf={
    "int":"%d",
    "float":"%f",
    "char*":"%s",
    "bool":"%d",
    "void":"%s",
    
}

help_dec=["#include <stdio.h>\n","#include <stdlib.h>\n","#include<stdbool.h>\n","#define ARRAYSIZE(arr) sizeof(arr) / sizeof(arr[0])\n"]