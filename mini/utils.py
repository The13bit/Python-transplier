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
                        pvars.append(type_to_printf[self.type_map[-1][ x[0]]])
                        
                        x=x[0]+''.join([f"[{i}]" for i in x[1:]])
                    else:
                        pvars.append(type_to_printf[self.type_map[-1][ x]])
                    args.append(x)
                    
                return "printf(\""+' '.join([f"{i} " for i in pvars])+"\\n\","+','.join(args)+")"
             
        
        elif isinstance(node,cst.Expr):
            x=self.get_basic_names(node.value)
            self.output.append(self.get_indent()+x+"\n")
            return None
        elif isinstance(node,cst.SimpleStatementLine):
            for i in node.body:
                self.get_basic_names(i)
            return True
        elif isinstance(node,cst.BinaryOperation):
            left=self.get_basic_names(node.left)
            right=self.get_basic_names(node.right)
            op=self.get_basic_names(node.operator)
            return f"{left} {op} {right}"
    
    