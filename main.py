import sys
from lexer import lex
from parser import parse

with open(sys.argv[1], 'r') as f:
    print("ACCEPT" if parse(lex(f.read())) else "REJECT")
