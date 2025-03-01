import ast
import sys

class ListCompTransformer(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign):
        # Only handle assignments with a single target that is a Name and list comprehensions
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.ListComp):
            target_name = node.targets[0].id
            list_comp = node.value

            new_nodes = []

            # Create: target = []
            new_assign = ast.Assign(
                targets=node.targets,
                value=ast.List(elts=[], ctx=ast.Load())
            )
            new_nodes.append(new_assign)

            # Build the inner append call: target.append(<elt>)
            append_call = ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=target_name, ctx=ast.Load()),
                        attr="append",
                        ctx=ast.Load()
                    ),
                    args=[list_comp.elt],
                    keywords=[]
                )
            )

            # Wrap the append call with nested loops and conditionals (if any)
            loop_body = append_call
            # Process generators in reverse order to nest them correctly
            for gen in reversed(list_comp.generators):
                # Wrap inner append call in if clauses if present
                inner_body = [loop_body]
                for if_cond in reversed(gen.ifs):
                    inner_body = [ast.If(test=if_cond, body=inner_body, orelse=[])]
                # Build the for loop for the current generator
                loop_body = ast.For(
                    target=gen.target,
                    iter=gen.iter,
                    body=inner_body,
                    orelse=[]
                )
            new_nodes.append(loop_body)
            # Replace the original assignment with new nodes (assignment + loop)
            return new_nodes
        return node

def transform_file(filename: str="./tst.py") -> None:
    with open(filename, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    transformer = ListCompTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    # Generate the updated source code using ast.unparse (Python 3.10+)
    new_source = ast.unparse(new_tree)
    print(new_source)

if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Usage: python transform_listcomps.py <python_file>")
    #     sys.exit(1)
    transform_file()