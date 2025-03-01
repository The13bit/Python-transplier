import ast
import sys

class Annotator(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Annotate all arguments if missing
        for arg in node.args.args:
            if arg.annotation is None:
                arg.annotation = ast.Name(id='Any', ctx=ast.Load())
        for arg in node.args.kwonlyargs:
            if arg.annotation is None:
                arg.annotation = ast.Name(id='Any', ctx=ast.Load())
        if node.args.vararg and node.args.vararg.annotation is None:
            node.args.vararg.annotation = ast.Name(id='Any', ctx=ast.Load())
        if node.args.kwarg and node.args.kwarg.annotation is None:
            node.args.kwarg.annotation = ast.Name(id='Any', ctx=ast.Load())

        # Annotate return type if missing
        if node.returns is None:
            node.returns = ast.Name(id='Any', ctx=ast.Load())

        self.generic_visit(node)
        return node

    def visit_Assign(self, node: ast.Assign):
        # Transform simple assignments with a single Name target
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            new_node = ast.AnnAssign(
                target=node.targets[0],
                annotation=ast.Name(id='Any', ctx=ast.Load()),
                value=node.value,
                simple=1
            )
            return ast.copy_location(new_node, node)
        return node

def add_any_import(tree: ast.Module) -> ast.Module:
    # Add 'from typing import Any' at the top if it's not already imported.
    has_any = False
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == 'typing':
            if any(alias.name == 'Any' for alias in node.names):
                has_any = True
                break
    if not has_any:
        import_any = ast.ImportFrom(
            module='typing',
            names=[ast.alias(name='Any', asname=None)],
            level=0
        )
        tree.body.insert(0, import_any)
    return tree

def annotate_file(filename: str) -> None:
    with open(filename, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    transformer = Annotator()
    new_tree = transformer.visit(tree)
    new_tree = add_any_import(new_tree)
    ast.fix_missing_locations(new_tree)
    new_source = ast.unparse(new_tree)
    print(new_source)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python annotator.py <python_file>")
        sys.exit(1)
    annotate_file(sys.argv[1])