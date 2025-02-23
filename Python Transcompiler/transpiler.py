import ast
import sys
from typing import Any, Dict, List, Optional, Set, Union
import textwrap
from CPPTransplier import CppTranspiler




def transpile_file(input_file: str, output_file: str) -> None:
    with open(input_file, 'r') as f:
        source = f.read()
    
    transpiler = CppTranspiler()
    cpp_code = transpiler.transpile(source)
    
    with open(output_file, 'w') as f:
        f.write(cpp_code)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python transpiler.py input.py output.cpp")
        sys.exit(1)
        
    transpile_file(sys.argv[1], sys.argv[2])