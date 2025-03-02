py_2_c_map={
    "int":"int",
    "float":"float",
    "str":"char*",
    "bool":"bool",
    "None":"void",
    "True":"true",
    "False":"false",
    
}

type_to_printf={
    "int":"%d",
    "float":"%f",
    "char*":"%s",
    "bool":"%d",
    "void":"%s",
    
}

help_dec=["#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))\n"]