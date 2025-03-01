import libcst as cst
import pathlib

from CParser import CParser
base= pathlib.Path(__file__).parent

file= open(str(base)+"/tst.py", "r").read()

tree=cst.parse_module(file)
# print(tree)
parser=CParser(tree)


print(parser.generate())