import libcst as cst
from .py2cmap import py_2_c_map, type_to_printf, help_dec
from .utils import basic_op, complex_op, assignments, get_name_or_vals
from collections import defaultdict


class CParser(cst.CSTVisitor):
    def __init__(self, node):
        super().__init__()
        self.output = []
        self.fun = []
        self.declared_fn = defaultdict()
        self.seen = set()
        self.type_map = [{}]
        self.indent = 0

        node.visit(self)

    def get_indent(self):
        return " " * self.indent * 4

    def generate(self):
        return "".join(help_dec) + "".join(self.fun) + "".join(self.output),self.declared_fn

    def get_basic_names(self, node):
        for i in [basic_op, assignments, get_name_or_vals, complex_op]:
            x = i(self, node)
            if x:
                return x

    def process_arr_ann(self, arr):
        n = len(arr) - 1
        dtype = py_2_c_map[arr[-1]]
        return dtype + "*" * n

    def visit_AnnAssign(self, node: cst.AnnAssign):
        if node in self.seen:
            return
        self.seen.add(node)
        target = self.get_basic_names(node.target)
        annotation = self.get_basic_names(node.annotation)
        if isinstance(annotation, list):
            self.type_map[-1][target] = py_2_c_map[annotation[-1]]

            if (
                isinstance(node.value, cst.BinaryOperation)
                and isinstance(node.value.operator, cst.Multiply)
                and isinstance(node.value.left, cst.List)
                
            ):
                if (
                    isinstance(node.value.right, cst.Call)
                    and isinstance(node.value.right.func, cst.Name)and len(node.value.left.elements) == 1
                    and node.value.right.func.value == "len"
                ):
                    #annotation = self.process_arr_ann(annotation)

                    # Extract the initial value and the length expression
                    init_value = self.get_basic_names(node.value.left.elements[0].value)
                    array_name = self.get_basic_names(node.value.right.args[0].value)

                    # Generate C array declaration and initialization loop
                    self.output.append(
                        self.get_indent()
                        + f"{annotation[-1]} {target}[ARRAYSIZE({array_name})];\n"
                    )
                    self.output.append(
                        self.get_indent()
                        + f"for(int i = 0; i < ARRAYSIZE({array_name}); i++) {{\n"
                    )
                    self.output.append(
                        self.get_indent() + f"    {target}[i] = {init_value};\n"
                    )
                    self.output.append(self.get_indent() + "}\n")
                    return
                elif isinstance(node.value.right, cst.Integer):
                    val=self.get_basic_names(node.value.right)
                    left=self.get_basic_names(node.value.left)
                    left=list(eval(left))[0]
                    #annotation=self.process_arr_ann(annotation)
                    self.output.append(
                        self.get_indent()
                        + f"{annotation[-1]} {target}[{val}];\n"
                    )
                    self.output.append(
                        self.get_indent()
                        + f"for(int i = 0; i < {val}; i++) {{\n"
                    )
                    self.output.append(
                        self.get_indent() + f"    {target}[i] = {left};\n"
                    )
                    self.output.append(self.get_indent() + "}\n")
                    return
                    
                        

            elif isinstance(node.value, cst.List):
                depth = len(annotation) - 2
                ln = depth
                tmp = node.value
                while depth:
                    tmp = tmp.elements[0].value
                    depth -= 1
                tmp = len(tmp.elements)

                value = self.get_basic_names(node.value)

                arr_dec = "[]" * ln + f"[{tmp}]"

                self.output.append(f"{annotation[-1]} {target}{arr_dec} = {value};\n")
                return

        else:
            annotation = py_2_c_map[annotation]
            self.type_map[-1][target] = annotation

        value = self.get_basic_names(node.value)

        self.output.append(self.get_indent() + f"{annotation}  {target} = {value};\n")

    def visit_Assign(self, node: cst.Assign):
        if node in self.seen:
            return
        self.seen.add(node)
        target = self.get_basic_names(node.targets[0])
        if isinstance(target, list):
            target = target[0] + "".join([f"[{i}]" for i in target[1:]])
        value = self.get_basic_names(node.value)
        self.output.append(self.get_indent() + f"{target} = {value};\n")

    def visit_IndentedBlock(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        self.indent += 1
        for i in node.body:
            self.get_basic_names(i)
        self.indent -= 1

    def visit_For(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        target = self.get_basic_names(node.target)
        iter = self.get_basic_names(node.iter)
        if "ARRAYSIZE" in iter:
            iter = iter[10:-2]
            
        cond = "<" if int(iter[2]) > 0 else ">"
        self.output.append(
            self.get_indent()
            + f"for(int {target}={iter[0]};{target}{cond}{iter[1]};{target}+={iter[2]})"
            + "{"
            + "\n"
        )
        node.body.visit(self)
        self.output.append(self.get_indent() + "}\n")

    def visit_AugAssign(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        target = self.get_basic_names(node.target)
        if isinstance(target, list):
            target = target[0] + ''.join([f"[{i}]" for i in target[1:]])
        value = self.get_basic_names(node.value)
        if isinstance(value, list):
            value = value[0] + ''.join([f"[{i}]" for i in value[1:]])
        op = self.get_basic_names(node.operator)
        self.output.append(self.get_indent() + f"{target} {op} {value};\n")

    def visit_If(self, node):
        if node in self.seen:
            return
        self.get_basic_names(node)

    def visit_Else(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        self.get_basic_names(node)

    def visit_FunctionDef(self, node):
        name = self.get_basic_names(node.name)
        params = self.get_basic_names(node.params)
        returns = self.get_basic_names(node.returns)

        if isinstance(returns, list):
            self.type_map[-1][name] = py_2_c_map[returns[-1]]
            returns = self.process_arr_ann(returns)
        else:
            returns = py_2_c_map[returns]

        tp = [i.split()[0] for i in params] if params else []
        self.declared_fn[(name,returns)]=tuple(tp)

        curr = len(self.output)
        if params:
            self.output.append(f"{returns} {name}(" + ", ".join(params) + ")" + "{\n")
        else:
            self.output.append(f"{returns} {name}()" + "{\n")
        node.body.visit(self)
        self.output.append("}\n")
        self.fun.extend(self.output[curr:])
        self.output = self.output[:curr]

    def visit_SimpleStatementLine(self, node):
        self.get_basic_names(node)
