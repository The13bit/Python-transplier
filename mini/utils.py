import libcst as cst

from py2cmap import py_2_c_map,type_to_printf
def basic_op(self,node):
    if isinstance(node,cst.Add):
           return "+"
    elif isinstance(node,cst.Divide):
        return "/"
    elif isinstance(node,cst.Subtract):
        return "-"
    elif isinstance(node,cst.Multiply):
        return "*"
    elif isinstance(node,cst.AddAssign):
        return "+="
    elif isinstance(node,cst.SubtractAssign):
        return "-="
    elif isinstance(node,cst.MultiplyAssign):
        return "*="
    elif isinstance(node,cst.DivideAssign):
        return "/="
    elif isinstance(node,cst.GreaterThan):
        return ">"
    elif isinstance(node,cst.GreaterThanEqual):
        return ">="
    elif isinstance(node,cst.LessThan):
        return "<"
    elif isinstance(node,cst.LessThanEqual):
        return "<="
    elif isinstance(node,cst.Equal):
        return "=="
    elif isinstance(node,cst.NotEqual):
        return "!="
    elif isinstance(node,cst.And):
        return "&&"
    elif isinstance(node,cst.Or):
        return "||"

def assignments(self,node):
        if isinstance(node,cst.Assign):
            node.visit(self)
            return True
        elif isinstance(node,cst.AnnAssign):
            node.visit(self)
            return True
        elif isinstance(node,cst.For):
            node.visit(self)
            return True
        elif isinstance(node,cst.AugAssign):
            node.visit(self)
            return True
        elif isinstance(node,cst.AssignTarget):
            return self.get_basic_names(node.target)

def get_name_or_vals(self,node):
        if isinstance(node,cst.Name):
            return node.value
        elif isinstance(node,cst.Attribute):
            return self.get_basic_names(node.value)+"."+node.attr.value
        elif isinstance(node,cst.Annotation):
            return self.get_basic_names(node.annotation)
        elif isinstance(node,cst.Integer):
            self.type_map[-1][node.value]="int"
            return node.value
        elif isinstance(node,cst.Arg):
            return self.get_basic_names(node.value)

def complex_op(self,node):
        if isinstance(node,cst.Subscript):
            x=self.get_basic_names(node.value)
            tmp=[]
            if isinstance(x,list):
                tmp+=x
            else:
                tmp.append(x)
            if node.slice:
                for i in node.slice:
                    x=self.get_basic_names(i)
                    if isinstance(x,list):
                        tmp.extend(x)
                    else:
                        tmp.append(x)
            return tmp
        elif isinstance(node,cst.SubscriptElement):
            return self.get_basic_names(node.slice)
        elif isinstance(node,cst.Index):
            return self.get_basic_names(node.value)
        elif isinstance(node,cst.List):
            tmp=[]
            if node.elements:
                for i in node.elements:
                    tmp.append(self.get_basic_names(i))
            
            return "{"+",".join(tmp)+"}"
        elif isinstance(node,cst.Element):
            return self.get_basic_names(node.value)
        

        elif isinstance(node,cst.Call):
            func=self.get_basic_names(node.func)
            if func=="range":
                vars=[0,0,1]
                if len(node.args)==1:
                    vars[1]=self.get_basic_names(node.args[0])
                elif len(node.args)==2:
                    vars[0]=self.get_basic_names(node.args[0])
                    vars[1]=self.get_basic_names(node.args[1])
                else:
                    for i in range(len(node.args)):
                        vars[i]=self.get_basic_names(node.args[i])
                return vars
            elif func=="print":
                args=[]
                pvars=[]
                for i in node.args:
                    x=self.get_basic_names(i)
                    if isinstance(x,list):
                        if x[0]=="!$#@!":
                            pvars.append(''.join(x[1]))
                            args.append(''.join(x[2]))
                            
                        elif x[0]=="$$!%#!":
                            pvars.append(x[1])
  

                            
                        else:
                            pvars.append(type_to_printf[self.type_map[-1][ x[0]]])
                        
                            x=x[0]+''.join([f"[{i}]" for i in x[1:]])
                            args.append(x)
                    else:
                        pvars.append(type_to_printf[self.type_map[-1][x]])
                        args.append(x)
                    
                    
                return "printf(\""+' '.join([f"{i} " for i in pvars])+"\\n\","+','.join(args)+")"
            elif func in self.declared_fn:
                args=[]
                for i in node.args:
                    x=self.get_basic_names(i)
                    if isinstance(x,list):
                        x=x[0]+''.join([f"[{i}]" for i in x[1:]])
                    args.append(x)
                return f"{func}({','.join(args)})"
            elif func=="len":
                return f"ARRAY_SIZE({self.get_basic_names(node.args[0])})"
             
        
        elif isinstance(node,cst.Expr):
            x=self.get_basic_names(node.value)
            self.output.append(self.get_indent()+x+"\n")
            return None
        elif isinstance(node,cst.SimpleStatementLine):
            if node in self.seen:
                return None
            self.seen.add(node)
            for i in node.body:
                self.get_basic_names(i)
            return True
        elif isinstance(node,cst.BinaryOperation):
            left=self.get_basic_names(node.left)
            if isinstance(left,list):
                left=left[0]+''.join([f"[{i}]" for i in left[1:]])
            right=self.get_basic_names(node.right)
            if isinstance(right,list):
                right=right[0]+''.join([f"[{i}]" for i in right[1:]])
            op=self.get_basic_names(node.operator)
            return f"{left} {op} {right}"
        elif isinstance(node,cst.If):
            test=self.get_basic_names(node.test)
            
            self.output.append(f"if({test})"+"{\n")
            node.body.visit(self)
            self.output.append(self.get_indent()+"}\n")
            if node.orelse:
                self.output.append("else ")
                
                node.orelse.visit(self)
              
        elif isinstance(node,cst.Else):
            self.output.append("{\n")
            node.body.visit(self)
            self.output.append(self.get_indent()+"}\n")
            
        elif isinstance(node,cst.BooleanOperation):
            left=self.get_basic_names(node.left)
            op=self.get_basic_names(node.operator)
            right=self.get_basic_names(node.right)
            if isinstance(left,list):
                left=left[0]+''.join([f"[{i}]" for i in left[1:]])
            if isinstance(right,list):
                right=right[0]+''.join([f"[{i}]" for i in right[1:]])
            
            
            
            return f"({left} {op} {right})"
        
        
        elif isinstance(node,cst.Comparison):
            target=self.get_basic_names(node.left)
            if isinstance(target,list):
                target=target[0]+''.join([f"[{i}]" for i in target[1:]])
            compare=self.get_basic_names(node.comparisons[0])
            
            return f"{target} {compare}"
        elif isinstance(node,cst.ComparisonTarget):
            
            op=self.get_basic_names(node.operator)
            comp=self.get_basic_names(node.comparator)
            
            return f"{op} {comp}"
        elif isinstance(node,cst.Param):
            name=self.get_basic_names(node.name)
            ann=self.get_basic_names(node.annotation)
            if isinstance(ann,list):
                ann=self.process_arr_ann(ann)
            
            return f"{ann} {name}"
        elif isinstance(node,cst.Parameters):
            tmp=[]
            if node.params:
                for i in node.params:
                    x=self.get_basic_names(i)
                    
                    tmp.append(x)
            return tmp
        elif isinstance(node,cst.Return):
            ret=self.get_basic_names(node.value)
            self.output.append(self.get_indent()+f"return {ret};\n")
        
        elif isinstance(node,cst.FormattedString):
            var=[]
            for i in node.parts:
                x=self.get_basic_names(i)
                var.append(x)
            s=[]
            arg=[]
            for i in var:
                if isinstance(i,list):
                    s.append(i[1])
                    arg.append(i[0])
                else:
                    s.append(i)
                
                
            return ["!$#@!",s,arg]
        
        elif isinstance(node,cst.FormattedStringText):
            return node.value
        elif isinstance(node,cst.FormattedStringExpression):
            val=self.get_basic_names(node.expression)
            sp=type_to_printf[self.type_map[-1][val]]
            return [val,sp]
        elif isinstance(node,cst.SimpleString):
            return ["$$!%#!",str(node.raw_value)]
            
            

    
    