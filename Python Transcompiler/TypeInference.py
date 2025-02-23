import ast
from typing import Dict, Set, Optional
from predefined_funcs import pre_def
class TypeInference:
    def __init__(self):
        self.type_map: Dict[str, str] = {
            'str': 'std::string',
            'int': 'int',
            'float': 'double',
            'bool': 'bool',
            'None': 'void'
        }
        self.imported_types: Set[str] = set()
        self.class_types: Dict[str, Dict[str, str]] = {}
        self.function_types: Dict[str, str] = {}
        self.wrapper_count = 0

    def add_function(self, name: str, return_type: str, params: Dict[str, str]) -> None:
        """Register a function's type information"""
        param_types = [ptype for ptype in params.values()]
        self.function_types[name] = f"std::function<{return_type}({', '.join(param_types)})>"

    def get_function_type(self, name: str) -> Optional[str]:
        """Get a function's type signature if registered"""
        return self.function_types.get(name)

   

    def resolve_type(self, type_str: str) -> str:
        """Resolve a type string to its C++ equivalent"""
        return self.type_map.get(type_str, type_str)

    def get_return_type(self, func_type: str) -> str:
        """Extract return type from a function type"""
        # Parse "std::function<return_type(param_types)>"
        if func_type.startswith("std::function<"):
            inner = func_type[len("std::function<"):-1]
            return inner[:inner.find("(")]
        return "auto"

    def create_wrapper_type(self, func_name: str) -> str:
        """Create a wrapper type for a decorated function"""
        self.wrapper_count += 1
        base_type = self.function_types.get(func_name, "auto")
        return f"Wrapper_{self.wrapper_count}<{base_type}>"

    def get_type(self, node: ast.AST) -> str:
       if isinstance(node, ast.Num):
           if isinstance(node.n, int):
               return "int"
           return "double"
       elif isinstance(node, ast.Str):
           return "std::string"
       elif isinstance(node, ast.List):
           if node.elts:
               elem_type = self.get_type(node.elts[0])
               return f"py::list<{elem_type}>"
           return "py::list<int>"
       elif isinstance(node, ast.Dict):
           if node.keys:
               key_type = self.get_type(node.keys[0])
               value_type = self.get_type(node.values[0])
               return f"py::dict<{key_type}, {value_type}>"
           return "py::dict<std::string, int>"
       elif isinstance(node, ast.Set):
           if node.elts:
               elem_type = self.get_type(node.elts[0])
               return f"py::set<{elem_type}>"
           return "py::set<int>"
       elif isinstance(node, ast.Tuple):
           if node.elts:
               types = [self.get_type(elt) for elt in node.elts]
               return f"std::tuple<{', '.join(types)}>"
           return "std::tuple<>"
       elif isinstance(node, ast.Name):
           if node.id in self.type_map:
               return self.type_map[node.id]
           if node.id in self.function_types:
               return self.function_types[node.id]
           return self.type_map.get(node.id, "auto")
       elif isinstance(node, ast.Call):
           if isinstance(node.func, ast.Name):
                if node.func.id == "range":
                   return "py::range"
                if node.func.id in self.function_types:
                   return self.get_return_type(self.function_types[node.func.id])
                if node.func.id in pre_def:
                    return self.get_type(ast.Set(node.args[0].elts))
       return "auto"