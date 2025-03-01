import libcst as cst
from py2cmap import py_2_c_map,type_to_printf
from utils import basic_op,complex_op,assignments,get_name_or_vals
class CParser(cst.CSTVisitor):
    def __init__(self,node):
        super().__init__()
        self.output=[]
        self.seen=set()
        self.type_map=[{}]
        self.indent=0
        
        node.visit(self)
        
    def get_indent(self):
        return " "*self.indent*4
    
    def generate(self):
        return "".join(self.output)    
    
    def get_basic_names(self,node):
        for i in [basic_op,assignments,get_name_or_vals,complex_op]:
            x=i(self,node)
            if x:
                return x
        
    
            
    def process_arr_ann(self,arr):
        n=len(arr)-1
        dtype=py_2_c_map[arr[-1]]
        return dtype+"*"*n
    def visit_AnnAssign(self, node:cst.AnnAssign):
        if node in self.seen:
            return
        self.seen.add(node)
        target=self.get_basic_names(node.target)
        annotation=self.get_basic_names(node.annotation)
        if isinstance(annotation,list):
            self.type_map[-1][target]=py_2_c_map[annotation[-1]]
            annotation=self.process_arr_ann(annotation)
        else:
            
            annotation=py_2_c_map[annotation]
            self.type_map[-1][target]=annotation
            
        
        value=self.get_basic_names(node.value)
        
        self.output.append(self.get_indent()+f"{annotation}  {target} = {value};\n")
    
    def visit_Assign(self, node:cst.Assign):
        if node in self.seen:
            return
        self.seen.add(node)
        target=self.get_basic_names(node.targets[0])
        if isinstance(target,list):
            target=target[0]+''.join([f"[{i}]" for i in target[1:]])
        value=self.get_basic_names(node.value)
        self.output.append(self.get_indent()+f"{target} = {value};\n")
    
    def visit_IndentedBlock(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        self.indent+=1
        for i in node.body:
            self.get_basic_names(i)
        self.indent-=1
        
    def visit_For(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        target=self.get_basic_names(node.target)
        iter=self.get_basic_names(node.iter)
        cond="<" if int(iter[2])>0 else ">"
        self.output.append(self.get_indent()+f"for(int {target}={iter[0]};{target}{cond}{iter[1]};{target}+={iter[2]})"+"{"+"\n")
        node.body.visit(self)
        self.output.append(self.get_indent()+"}\n")
    
    def visit_AugAssign(self, node):
        if node in self.seen:
            return
        self.seen.add(node)
        target=self.get_basic_names(node.target)
        value=self.get_basic_names(node.value)
        op=self.get_basic_names(node.operator)
        self.output.append(self.get_indent()+f"{target} {op} {value};\n")

    
    