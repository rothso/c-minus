
import sys
from lexer import lex
from parser import parse
from semantics import analyze

with open(sys.argv[1], 'r') as f:
    print("ACCEPT" if analyze(parse(lex(f.read()))) else "REJECT")