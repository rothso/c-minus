
import sys
from lexer import lex
from parser import parse
from semantics import analyze
from codegen import to_ir

with open(sys.argv[1], 'r') as f:
    [print(line) for line in to_ir(analyze(parse(lex(f.read()))))]
