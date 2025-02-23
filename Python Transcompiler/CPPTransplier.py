import ast
import sys
from typing import Any, Dict, List, Optional, Set, Union
from predefined_funcs import pre_def
import textwrap
from TypeInference import TypeInference
op_map = {
                ast.Add: "+",
                ast.Sub: "-",
                ast.Mult: "*",
                ast.Div: "/",
                ast.FloorDiv: "/",
                ast.Mod: "%",
                ast.Pow: "pow",
                ast.BitOr: "|",
                ast.BitAnd: "&",
                ast.BitXor: "^"
            }

eq_map={
                ast.Eq: "==",
                ast.NotEq: "!=",
                ast.Lt: "<",
                ast.LtE: "<=",
                ast.Gt: ">",
                ast.GtE: ">="
            }
class CppTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.indentation = 0
        self.type_inference = [TypeInference()]
        self.imports: Dict[str, str] = {}
        self.output: List[str] = []
        self.fn_out:List[str]=[]
        self.current_class: Optional[str] = None
        self.in_function = False
        self.temp_var_count = 0
        self.try_count = 0
        self.includes = set([
            "<iostream>",
            "<string>",
            "<vector>",
            "<unordered_map>",
            "<unordered_set>",
            "<functional>",
            "<memory>",
            "<cmath>",
            "<stdexcept>",
            "<tuple>",
            "<sstream>",
            "<fstream>",
            "\"runtime.hpp\"",
            
        ])
    def check_existence(self,id)->bool:
        for i in self.type_inference:
            if id in i.type_map:
                return True
        return False
    def indent(self) -> str:
        return "    " * self.indentation
    def find_type(self,node:ast.AST)->str:
        res=""
        
        for i in self.type_inference:
            x=i.get_type(node)
            if x!="auto":
                res=x
                break
        return res if res else "auto"
                
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module
        for name in node.names:
            self.imports[name.name] = module

    def handle_docstring(self, node: ast.FunctionDef) -> None:
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Str)):
            docstring = node.body[0].value.s
            self.output.append(f"{self.indent()}// {docstring}")
            return node.body[1:]
        return node.body

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Skip if this is a class method (handled by visit_ClassDef)
        if self.current_class:
            return

        self.in_function = True
        
        # Handle docstring
        body = self.handle_docstring(node)
        
        # Determine return type
        return_type = "auto"
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = self.type_inference[-1].resolve_type(node.returns.id)

        # Process parameters
        params = []
        for arg in node.args.args:
            arg_type = "auto"
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    arg_type = self.type_inference[-1].resolve_type(arg.annotation.id)
            params.append(f"{arg_type} {arg.arg}")

        # Generate function declaration
        print(f"\n{self.indent()}{return_type} {node.name}({', '.join(params)}) {{")
        slice_len=len(self.output)
        self.output.append(f"\n{self.indent()}{return_type} {node.name}({', '.join(params)}) {{")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        # Process function body
        for stmt in body:
            self.visit(stmt)
        self.type_inference.pop()
        self.indentation -= 1
        self.output.append(f"{self.indent()}}}\n")
        if self.output[slice_len-1].startswith("//"):
            slice_len-=1
        self.fn_out+=self.output[slice_len:]
        self.output=self.output[:slice_len]
        self.in_function = False

    def visit_Try(self, node: ast.Try) -> None:
        scope_name = f"try_scope_{self.try_count}"
        self.try_count += 1
        
        # Create a scope for try block
        self.output.append(f"{self.indent()}{{  // try block {scope_name}")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        # Try block
        for stmt in node.body:
            self.visit(stmt)
        self.type_inference.pop()
        self.indentation -= 1
        
        # Handle except blocks
        for handler in node.handlers:
            if handler.type:
                exc_type = handler.type.id if isinstance(handler.type, ast.Name) else "std::exception"
                self.output.append(f"{self.indent()}}}")
                self.output.append(f"{self.indent()}catch (const {exc_type}& e) {{")
                self.indentation += 1
                
                for stmt in handler.body:
                    self.visit(stmt)
                    
                self.indentation -= 1
        
        # Handle finally block
        if node.finalbody:
            self.output.append(f"{self.indent()}}}")
            self.output.append(f"{self.indent()}catch (...) {{")
            self.indentation += 1
            
            for stmt in node.finalbody:
                self.visit(stmt)
                
            self.output.append(f"{self.indent()}throw;")
            self.indentation -= 1
            
        self.output.append(f"{self.indent()}}}")

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name):
                if item.context_expr.func.id == "open":
                    file_var = self.visit_expr(item.optional_vars)
                    filename = self.visit_expr(item.context_expr.args[0])
                    mode = self.visit_expr(item.context_expr.args[1]) if len(item.context_expr.args) > 1 else '"r"'
                    
                    self.output.append(f"{self.indent()}{{  // file scope")
                    self.output.append(f"{self.indent()}    py::file {file_var}({filename}, {mode});")
                    self.indentation += 1
                    self.type_inference.append(TypeInference())
                    for stmt in node.body:
                        self.visit(stmt)
                    self.type_inference.pop()
                    self.indentation -= 1
                    self.output.append(f"{self.indent()}}}")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = node.name
        self.current_class = class_name
        self.type_inference[-1].class_types[class_name] = {}

        # Start class definition
        self.output.append(f"{self.indent()}class {class_name} {{")
        self.output.append(f"{self.indent()}public:")
        self.indentation += 1

        # First pass: collect member variables
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                var_name = stmt.target.id
                var_type = self.type_inference[-1].resolve_type(
                    stmt.annotation.id if isinstance(stmt.annotation, ast.Name) else "auto"
                )
                self.type_inference[-1].class_types[class_name][var_name] = var_type
                self.output.append(f"{self.indent()}{var_type} {var_name};")

        # Second pass: process methods
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                body = self.handle_docstring(stmt)
                is_init = stmt.name == "__init__"
                method_name = class_name if is_init else stmt.name
                return_type = "void" if is_init else (
                    self.type_inference[-1].resolve_type(stmt.returns.id)
                    if stmt.returns else "auto"
                )

                if is_init:
                    self.visit_init(stmt, body)
                else:
                    self.visit_method(stmt, return_type, body)

        self.indentation -= 1
        self.output.append(f"{self.indent()}}};")
        self.current_class = None

    def visit_init(self, node: ast.FunctionDef, body: List[ast.AST]) -> None:
        params = []
        for arg in node.args.args:
            if arg.arg != "self":
                arg_type = self.type_inference[-1].resolve_type(
                    arg.annotation.id if arg.annotation else "auto"
                )
                params.append(f"{arg_type} {arg.arg}")

        self.output.append(f"{self.indent()}{self.current_class}({', '.join(params)}) {{")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        for stmt in body:
            self.visit(stmt)
        self.type_inference.pop()
        self.indentation -= 1
        self.output.append(f"{self.indent()}}}")

    def visit_method(self, node: ast.FunctionDef, return_type: str, body: List[ast.AST]) -> None:
        params = []
        for arg in node.args.args:
            if arg.arg != "self":
                arg_type = self.type_inference[-1].resolve_type(
                    arg.annotation.id if arg.annotation else "auto"
                )
                params.append(f"{arg_type} {arg.arg}")

        self.output.append(f"{self.indent()}{return_type} {node.name}({', '.join(params)}) {{")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        for stmt in body:
            self.visit(stmt)
        self.type_inference.pop()
        self.indentation -= 1
        self.output.append(f"{self.indent()}}}")

    def visit_Assign(self, node: ast.Assign) -> None:
        target = node.targets[0]
        value = node.value

        if isinstance(target, ast.Name):
            var_type = self.find_type(value)
            if not  self.check_existence(target.id):
                self.type_inference[-1].type_map[target.id] = var_type
                self.output.append(f"{self.indent()}{var_type} {target.id} = {self.visit_expr(value)};")
            else:
                self.output.append(f"{self.indent()}{target.id} = {self.visit_expr(value)};")
        elif isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name) and target.value.id == "self":
                self.output.append(f"{self.indent()}{target.attr} = {self.visit_expr(value)};")
            else:
                self.output.append(f"{self.indent()}{self.visit_expr(target)} = {self.visit_expr(value)};")

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        target = node.target
        if isinstance(target, ast.Name):
            type_annotation = self.type_inference[-1].resolve_type(
                node.annotation.id if isinstance(node.annotation, ast.Name) else "auto"
            )
            value_str = self.visit_expr(node.value) if node.value else ""
            self.type_inference[-1].type_map[target.id] = type_annotation
            self.output.append(f"{self.indent()}{type_annotation} {target.id}{' = ' + value_str if value_str else ''};")

    def visit_If(self, node: ast.If) -> None:
        self.output.append(f"{self.indent()}if ({self.visit_expr(node.test)}) {{")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        
        

        for stmt in node.body:
            self.visit(stmt)
        
        self.type_inference.pop()

        self.indentation -= 1

        if node.orelse:
            self.output.append(f"{self.indent()}}} else {{")
            self.indentation += 1

            for stmt in node.orelse:
                self.visit(stmt)

            self.indentation -= 1

        self.output.append(f"{self.indent()}}}")

    def visit_For(self, node: ast.For) -> None:
        iter_expr = node.iter
        target = self.visit_expr(node.target)
        
        if isinstance(iter_expr, ast.Call) and isinstance(iter_expr.func, ast.Name) and iter_expr.func.id == "range":
            if len(iter_expr.args) == 1:
                args = f"0, {self.visit_expr(iter_expr.args[0])}"
            elif len(iter_expr.args) == 2:
                args = f"{self.visit_expr(iter_expr.args[0])}, {self.visit_expr(iter_expr.args[1])}"
            else:
                args = f"{self.visit_expr(iter_expr.args[0])}, {self.visit_expr(iter_expr.args[1])}, {self.visit_expr(iter_expr.args[2])}"
            
            self.output.append(f"{self.indent()}for (const auto {target} : py::range({args})) {{")
        else:
            iter_type = self.find_type(iter_expr)
            self.output.append(f"{self.indent()}for (const auto& {target} : {self.visit_expr(iter_expr)}) {{")

        self.indentation += 1
        self.type_inference.append(TypeInference())
        for stmt in node.body:
            self.visit(stmt)
        self.type_inference.pop()
        self.indentation -= 1
        self.output.append(f"{self.indent()}}}")

    def visit_While(self, node: ast.While) -> None:
        self.output.append(f"{self.indent()}while ({self.visit_expr(node.test)}) {{")
        self.indentation += 1
        self.type_inference.append(TypeInference())
        for stmt in node.body:
            self.visit(stmt)    
        self.type_inference.pop()

        self.indentation -= 1
        self.output.append(f"{self.indent()}}}")
    def visit_AugAssign(self, node):
        target=self.visit_expr(node.target)
        value=self.visit_expr(node.value)
        op=op_map[type(node.op)]
        self.output.append(f"{self.indent()}{target} {op}= {value};")
        
        
    def visit_ListComp(self, node: ast.ListComp) -> str:
        result_var = f"_listcomp_{self.temp_var_count}"
        self.temp_var_count += 1

        element_type = self.find_type(node.elt)
        self.output.append(f"{self.indent()}py::list<{element_type}> {result_var};")

        for generator in node.generators:
            iter_expr = self.visit_expr(generator.iter)
            target = self.visit_expr(generator.target)

            self.output.append(f"{self.indent()}for (const auto& {target} : {iter_expr}) {{")
            self.indentation += 1

            for condition in generator.ifs:
                self.output.append(f"{self.indent()}if ({self.visit_expr(condition)}) {{")
                self.indentation += 1

        self.output.append(f"{self.indent()}{result_var}.append({self.visit_expr(node.elt)});")

        for generator in node.generators:
            for _ in generator.ifs:
                self.indentation -= 1
                self.output.append(f"{self.indent()}}}")
            self.indentation -= 1
            self.output.append(f"{self.indent()}}}")

        return result_var

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> str:
        return self.visit_ListComp(ast.ListComp(elt=node.elt, generators=node.generators))

    def visit_Return(self, node: ast.Return) -> None:
        if node.value:
            self.output.append(f"{self.indent()}return {self.visit_expr(node.value)};")
        else:
            self.output.append(f"{self.indent()}return;")

    def visit_Expr(self, node: ast.Expr) -> None:
        expr = self.visit_expr(node.value)
        if expr and not isinstance(node.value, ast.Str):  # Skip standalone string literals (docstrings)
            self.output.append(f"{self.indent()}{expr};")

    def format_string(self, node: ast.JoinedStr) -> str:
        parts = []
        for value in node.values:
            if isinstance(value, ast.Str):
                parts.append(f'"{value.s}"')
            elif isinstance(value, ast.FormattedValue):
                expr = self.visit_expr(value.value)
                # For string types, use directly, otherwise use to_string
                if isinstance(value.value, (ast.Str, ast.JoinedStr)) or (
                    isinstance(value.value, ast.Name) and 
                    self.find_type(value.value) == "std::string"
                ):
                    parts.append(expr)
                else:
                    parts.append(f"std::to_string({expr})")
        return ' + '.join(parts)

    def visit_expr(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        
        elif isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.Str):
            return f'"{node.s}"'
        elif isinstance(node, ast.JoinedStr):
            return self.format_string(node)
        elif isinstance(node, ast.BinOp):
            left = self.visit_expr(node.left)
            right = self.visit_expr(node.right)
            
            op = op_map[type(node.op)]
            if isinstance(node.op, ast.Pow):
                return f"std::pow({left}, {right})"
            elif isinstance(node.op, ast.FloorDiv):
                return f"std::floor({left} / static_cast<double>({right}))"
            return f"({left} {op} {right})"
        elif isinstance(node, ast.Compare):
            #ADD support for and or 
            left = self.visit_expr(node.left)
            
            ops = [eq_map[type(op)] for op in node.ops]
            comparators = [self.visit_expr(comp) for comp in node.comparators]
            if len(ops) == 1:
                return f"({left} {ops[0]} {comparators[0]})"
            else:
                return " && ".join([f"({left} {op} {comp})" for op, comp in zip(ops, comparators)])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "print":
                    args = [self.visit_expr(arg) for arg in node.args]
                    return f"std::cout << {' << " " << '.join(args)} << std::endl"
                elif node.func.id == "len":
                    return f"({self.visit_expr(node.args[0])}).size()"
                elif node.func.id in self.imports:
                    return f"{node.func.id}({', '.join(self.visit_expr(arg) for arg in node.args)})"
                elif node.func.id in pre_def:
                    return self.visit_expr(pre_def[node.func.id](node.args[0].elts))
            return f"{self.visit_expr(node.func)}({', '.join(self.visit_expr(arg) for arg in node.args)})"
        elif isinstance(node, ast.List):
            elements = [self.visit_expr(elt) for elt in node.elts]
            if not elements:
                return "py::list<int>()"
            return f"py::list<{self.find_type(node.elts[0])}>({{{', '.join(elements)}}})"
        elif isinstance(node, ast.Dict):
            items = []
            for k, v in zip(node.keys, node.values):
                key = self.visit_expr(k)
                value = self.visit_expr(v)
                items.append(f"{{{key}, {value}}}")
            if not items:
                return "py::dict<std::string, int>()"
            return f"py::dict<{self.find_type(node.keys[0])}, {self.find_type(node.values[0])}>({{{', '.join(items)}}})"
        elif isinstance(node, ast.Set):
            elements = [self.visit_expr(elt) for elt in node.elts]
            if not elements:
                return "py::set<int>()"
            return f"py::set<{self.find_type(node.elts[0])}>({{{', '.join(elements)}}})"
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                return node.attr
            return f"{self.visit_expr(node.value)}.{node.attr}"
        elif isinstance(node, ast.ListComp):
            return self.visit_ListComp(node)
        elif isinstance(node, ast.Lambda):
            args = [arg.arg for arg in node.args.args]
            body = self.visit_expr(node.body)
            return f"[=]({', '.join('const auto& ' + arg for arg in args)}) {{ return {body}; }}"
        elif isinstance(node, ast.Tuple):
            elements = [self.visit_expr(elt) for elt in node.elts]
            return f"std::make_tuple({', '.join(elements)})"
        elif isinstance(node,ast.Constant):
            if node.n==None:
                return "nullptr"
            elif isinstance(node.n,bool):
                return str(node.n).lower()

        return str(node)

    def transpile(self, source: str) -> str:
        tree = ast.parse(source)
        self.generic_visit(tree)

        # Generate includes
        includes = "\n".join(f"#include {inc}" for inc in sorted(self.includes))
        
        # Generate the main function wrapper
        if not any(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body):
            output_with_main = self.output[:]
            self.output = []
            self.output.append("using namespace py;")
            self.output.append("")
            if self.fn_out:
                self.output+=self.fn_out
            self.output.append("int main() {")
            self.indentation = 1
            for line in output_with_main:
                if not line.strip().startswith("auto "):  # Skip forward declarations
                    self.output.append(self.indent() + line)
            self.indentation = 0
            self.output.append("    return 0;")
            self.output.append("}")
        
        return f"""{includes}

{chr(10).join(self.output)}"""