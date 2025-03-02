from math import e
import libcst as cst

from py2cmap import py_2_c_map, type_to_printf

# Function to translate Python operators to their C equivalents
def basic_op(self, node):
    if isinstance(node, cst.Add):
        return "+"
    elif isinstance(node, cst.Divide):
        return "/"
    elif isinstance(node, cst.Subtract):
        return "-"
    elif isinstance(node, cst.Multiply):
        return "*"
    elif isinstance(node, cst.AddAssign):
        return "+="
    elif isinstance(node, cst.SubtractAssign):
        return "-="
    elif isinstance(node, cst.MultiplyAssign):
        return "*="
    elif isinstance(node, cst.DivideAssign):
        return "/="
    elif isinstance(node, cst.GreaterThan):
        return ">"
    elif isinstance(node, cst.GreaterThanEqual):
        return ">="
    elif isinstance(node, cst.LessThan):
        return "<"
    elif isinstance(node, cst.LessThanEqual):
        return "<="
    elif isinstance(node, cst.Equal):
        return "=="
    elif isinstance(node, cst.NotEqual):
        return "!="
    elif isinstance(node, cst.And):
        return "&&"
    elif isinstance(node, cst.Or):
        return "||"
    elif isinstance(node, cst.Not):
        return "!"
    elif isinstance(node, cst.Modulo):
        return "%"
    elif isinstance(node, cst.BitAnd):
        return "&"
    elif isinstance(node, cst.BitOr):
        return "|"
    elif isinstance(node, cst.BitXor):
        return "^"
    elif isinstance(node, cst.Minus):
        return "-"

# Function to handle different types of assignment statements
def assignments(self, node):
    if isinstance(node, cst.Assign):
        node.visit(self)
        return True
    elif isinstance(node, cst.AnnAssign):
        node.visit(self)
        return True
    elif isinstance(node, cst.For):
        node.visit(self)
        return True
    elif isinstance(node, cst.AugAssign):
        node.visit(self)
        return True
    elif isinstance(node, cst.AssignTarget):
        return self.get_basic_names(node.target)

# Function to extract names or values from different types of nodes
def get_name_or_vals(self, node):
    if isinstance(node, cst.Name):
        return node.value
    elif isinstance(node, cst.Attribute):
        return self.get_basic_names(node.value) + "." + node.attr.value
    elif isinstance(node, cst.Annotation):
        return self.get_basic_names(node.annotation)
    elif isinstance(node, cst.Integer):
        self.type_map[-1][node.value] = "int"
        return node.value
    elif isinstance(node, cst.Float):
        self.type_map[-1][node.value] = "float"
        return node.value
    elif isinstance(node, cst.Arg):
        return self.get_basic_names(node.value)

# Function to handle complex operations and statements
def complex_op(self, node):
    # Handle subscripts (array indexing)
    if isinstance(node, cst.Subscript):
        x = self.get_basic_names(node.value)
        tmp = []
        if isinstance(x, list):
            tmp += x
        else:
            tmp.append(x)
        if node.slice:
            for i in node.slice:
                x = self.get_basic_names(i)
                if isinstance(x, list):
                    tmp.extend(x)
                else:
                    tmp.append(x)
        return tmp
    elif isinstance(node, cst.SubscriptElement):
        return self.get_basic_names(node.slice)
    elif isinstance(node, cst.Index):
        return self.get_basic_names(node.value)
    # Handle list literals
    elif isinstance(node, cst.List):
        tmp = []
        if node.elements:
            for i in node.elements:
                tmp.append(self.get_basic_names(i))
        
        return "{" + ",".join(tmp) + "}"
    elif isinstance(node, cst.Element):
        return self.get_basic_names(node.value)
    
    # Handle function calls
    elif isinstance(node, cst.Call):
        func = self.get_basic_names(node.func)
        # Special handling for built-in functions
        if func == "range":
            # Convert Python range to C for loop parameters (start, stop, step)
            vars = [0, 0, 1]
            if len(node.args) == 1:
                vars[1] = self.get_basic_names(node.args[0])
            elif len(node.args) == 2:
                vars[0] = self.get_basic_names(node.args[0])
                vars[1] = self.get_basic_names(node.args[1])
            else:
                for i in range(len(node.args)):
                    vars[i] = self.get_basic_names(node.args[i])
            return vars
        elif func == "print":
            # Convert Python print to C printf
            args = []
            pvars = []  # Format specifiers
            for i in node.args:
                x = self.get_basic_names(i)
                if isinstance(x, list):
                    if x[0] == "!$#@!":
                        # Formatted string handling
                        pvars.append(''.join(x[1]))
                        args.append(''.join(x[2]))
                        
                    elif x[0] == "$$!%#!":
                        # Raw string handling
                        pvars.append(x[1])
                    else:
                        # Array handling
                        pvars.append(type_to_printf[self.type_map[-1][x[0]]])
                        x = x[0] + ''.join([f"[{i}]" for i in x[1:]])
                        args.append(x)
                else:
                    # Function call argument handling
                    if isinstance(x, str) and '(' in x and x.endswith(')'):
                        # Extract just the function name for type lookup
                        func_name = x.split('(')[0]
                        pvars.append(type_to_printf[self.type_map[-1][func_name]])
                    else:
                        pvars.append(type_to_printf[self.type_map[-1][x]])
                    args.append(x)
            
            return "printf(\"" + ' '.join([f"{i} " for i in pvars]) + "\\n\"," + ','.join(args) + ");"
        elif func in self.declared_fn:
            # Handle user-defined function calls
            args = []
            for i in node.args:
                x = self.get_basic_names(i)
                if isinstance(x, list):
                    x = x[0] + ''.join([f"[{i}]" for i in x[1:]])
                args.append(x)
            return f"{func}({','.join(args)})"
        elif func == "len":
            # Convert Python len function to C macro
            return f"ARRAYSIZE(&{self.get_basic_names(node.args[0])})"
         
    # Handle expressions and statements
    elif isinstance(node, cst.Expr):
        x = self.get_basic_names(node.value)
        self.output.append(self.get_indent() + x + "\n")
        return None
    elif isinstance(node, cst.SimpleStatementLine):
        # Avoid processing already seen nodes
        if node in self.seen:
            return None
        self.seen.add(node)
        for i in node.body:
            self.get_basic_names(i)
        return True
    elif isinstance(node, cst.BinaryOperation):
        # Handle binary operations (e.g., a + b)
        left = self.get_basic_names(node.left)
        if isinstance(left, list):
            left = left[0] + ''.join([f"[{i}]" for i in left[1:]])
        right = self.get_basic_names(node.right)
        if isinstance(right, list):
            right = right[0] + ''.join([f"[{i}]" for i in right[1:]])
        op = self.get_basic_names(node.operator)
        return f"{left} {op} {right}"
    elif isinstance(node, cst.If):
        # Convert Python if statement to C
        test = self.get_basic_names(node.test)
        
        self.output.append(f"if({test})" + "{\n")
        node.body.visit(self)
        self.output.append(self.get_indent() + "}\n")
        if node.orelse:
            self.output.append("else ")
            node.orelse.visit(self)
    elif isinstance(node, cst.Else):
        # Convert Python else statement to C
        self.output.append("{\n")
        node.body.visit(self)
        self.output.append(self.get_indent() + "}\n")
        
    elif isinstance(node, cst.BooleanOperation):
        # Handle boolean operations (and, or)
        left = self.get_basic_names(node.left)
        op = self.get_basic_names(node.operator)
        right = self.get_basic_names(node.right)
        if isinstance(left, list):
            left = left[0] + ''.join([f"[{i}]" for i in left[1:]])
        if isinstance(right, list):
            right = right[0] + ''.join([f"[{i}]" for i in right[1:]])
        
        return f"({left} {op} {right})"
    
    elif isinstance(node, cst.Comparison):
        # Handle comparisons (e.g., a > b)
        target = self.get_basic_names(node.left)
        if isinstance(target, list):
            target = target[0] + ''.join([f"[{i}]" for i in target[1:]])
        compare = self.get_basic_names(node.comparisons[0])
        
        return f"{target} {compare}"
    elif isinstance(node, cst.ComparisonTarget):
        # Process the right side of a comparison
        op = self.get_basic_names(node.operator)
        comp = self.get_basic_names(node.comparator)
        
        return f"{op} {comp}"
    elif isinstance(node, cst.Param):
        # Convert Python function parameters to C
        name = self.get_basic_names(node.name)
        ann = self.get_basic_names(node.annotation)
        if isinstance(ann, list):
            ann = self.process_arr_ann(ann)
        
        return f"{ann} {name}"
    elif isinstance(node, cst.Parameters):
        # Process all parameters of a function
        tmp = []
        if node.params:
            for i in node.params:
                x = self.get_basic_names(i)
                tmp.append(x)
        return tmp
    elif isinstance(node, cst.Return):
        # Convert Python return statement to C
        ret = self.get_basic_names(node.value)
        self.output.append(self.get_indent() + f"return {ret};\n")
    
    elif isinstance(node, cst.FormattedString):
        # Handle f-strings
        var = []
        for i in node.parts:
            x = self.get_basic_names(i)
            var.append(x)
        s = []
        arg = []
        for i in var:
            if isinstance(i, list):
                s.append(i[1])
                arg.append(i[0])
            else:
                s.append(i)
        
        return ["!$#@!", s, arg]
    
    elif isinstance(node, cst.FormattedStringText):
        # Plain text in f-strings
        return node.value
    elif isinstance(node, cst.FormattedStringExpression):
        # Expressions in f-strings
        val = self.get_basic_names(node.expression)
        sp = type_to_printf[self.type_map[-1][val]]
        return [val, sp]
    elif isinstance(node, cst.SimpleString):
        # Process regular strings
        return ["$$!%#!", str(node.raw_value)]
    elif isinstance(node,cst.UnaryOperation):
        # Handle unary operations
        op = self.get_basic_names(node.operator)
        val = self.get_basic_names(node.expression)
        return f"{op}{val}"