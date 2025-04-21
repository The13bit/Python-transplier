from sqlite3 import paramstyle
import time
import libcst as cst
import numba
from zipp import Path
from mini.CParser import CParser
import inspect
import hashlib
import ctypes
import pathlib
import json
import subprocess
import os
from numba import jit
import numpy as np
base=pathlib.Path(__file__).parent/"compiled_fns"

loaded={}
overhead={}


type_to_ctype={
    "int":ctypes.c_int,
    "float":ctypes.c_float,
    "str":ctypes.c_char_p,
    
}
def array_converter(arr,depth,c_type):
    rows=len(arr)
    
    if depth==1:
        
        r_type=c_type*rows
        r_arr=r_type(*arr)
        return r_arr,r_type
    cols=len(arr[0])
    r_type=None
    tmp=[]
    
    for i in arr:
        if len(i)!=cols:
            raise ValueError("All rows should have same number of columns")
        t_arr,t_type=array_converter(i,depth-1,c_type)
        if not r_type:
            r_type=ctypes.POINTER(t_type)
        tmp.append(ctypes.cast(t_arr,r_type))
        
    r_arr=(r_type*rows)(*tmp)
    return r_arr,r_type
def met():
    time.sleep(0.001)
def to_sc(fn):
    #use numba jit
    def wrap(*args):
        return jit(fn)(*args)
        
    return wrap          

    
#decorator that  wrpas a fun and converts it to C
def to_c(dbg=False):
    def faster(fn):

        base.mkdir(exist_ok=True)
        (base/"Intermediate").mkdir(exist_ok=True)
        (base/"compiled").mkdir(exist_ok=True)
        if not os.path.exists(base/"compiled_fns.json"):
            with open(base/"compiled_fns.json", "w") as f:
                json.dump({}, f)
        with open(base/"compiled_fns.json", "r") as f:
            data=json.load(f)

    

        src=inspect.getsource(fn)
        ck=hashlib.md5(src.encode()).hexdigest()
        function_tps = None
        if  ck not in data:
        
            tree=cst.parse_module(src)
            parser=CParser(tree)
            out,tps=parser.generate()

            #print(tps)
            with open(str(base/"Intermediate"/f"{ck}.c"), "w") as f:
                f.write(out)
            data[ck]={"$":{f"{list(tps.keys())[0]}":f"{list(tps.values())[0]}"},"compiled":False}
            with open(base/"compiled_fns.json", "w") as f:
                json.dump(data, f)
        if not data[ck]["compiled"]:
            print(["gcc", "-g",  "-shared", "-o", f"{base/"compiled"/f"{ck}.so"}", "-fPIC",  f"{base/'Intermediate'/f'{ck}.c'}"])
            proc=subprocess.run(["gcc", "-g",  "-shared", "-o", f"{base/"compiled"/f"{ck}.so"}", "-fPIC",  f"{base/'Intermediate'/f'{ck}.c'}"])
            if proc.returncode:
                raise ValueError("Error in compilation")
            data[ck]["compiled"]=True
            with open(base/"compiled_fns.json", "w") as f:
                json.dump(data, f)
            #os.system(f"gcc -g  -shared -o {base/"compiled"/f"{ck}.so"} -fPIC  {base/'Intermediate'/f'{ck}.c'}")
        function_tps=data[ck]["$"]
        def wrapper(*args):

            ret,params=eval(list(function_tps.keys())[0]),eval(list(function_tps.values())[0])

            c_arg_arr=[]

            py_params=[]
            py_result_params = []  # Will hold Python-friendly versions
            pointer_indices = []  # Track which parameters are pointers
            c_ret="None"

            for inx,i in enumerate(params):
                if "*" in i:
                    tmp=type_to_ctype[i.replace("*", "").strip()]
                    cnt=i.count("*")
                    t_arr,t_type=array_converter(args[inx],cnt,tmp)
                    c_arg_arr.append(ctypes.POINTER(t_type))
                    py_params.append(t_arr)
                    pointer_indices.append(inx)


                else:
                    c_arg_arr.append(type_to_ctype[i])
                    py_params.append(args[inx])
            ret=ret[1]
            if ck not in loaded:
                lib=ctypes.CDLL(str(base/"compiled"/f"{ck}.so"))
                function_name = fn.__name__
                lib_function = getattr(lib, function_name)
                
                if ret!="void":
                    c_ret=type_to_ctype[ret]

                    lib_function.restype = c_ret
                loaded[ck]=lib_function
            lib_function=loaded[ck]
            lib_function.argtypes=c_arg_arr
                

            res=lib_function(*py_params)
            start=time.time()
            for i, inx in enumerate(pointer_indices):
                orig_dims = _get_dimensions(args[inx])
                py_result_params.append(_pointer_to_list(py_params[inx], orig_dims))
            if dbg:
                overhead[0]=overhead.get(0,0)+time.time()-start
                #print(f"Overhead: {overhead[0]}")
                
            if ret!="void":
                return res
            return py_result_params[-1]
            #return res, py_result_params  # Return both the original result and converted parameters

        return wrapper
    return faster

def _get_dimensions(arr):
    """Get dimensions of a nested list"""
    dims = []
    current = arr
    while isinstance(current, list):
        dims.append(len(current))
        if current:
            current = current[0]
        else:
            break
    return dims


def _pointer_to_list(ptr, dims, depth=0):
    """Convert a C pointer back to a Python list based on original dimensions"""
    if len(dims) == 1:
        return [ptr[i] for i in range(dims[0])]
    if depth == len(dims)-1:
        return [ptr[0][i] for i in range(dims[depth])]
    
    result = []
    for i in range(dims[depth]):
        result.append(_pointer_to_list(ptr[i], dims, depth + 1))
    return result
    
    