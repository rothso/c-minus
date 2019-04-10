import sys
from lexer import lex
from parser import parse
from semantics import analyze
from codegen import to_ir


def display(num, line):
    instruction, source1, source2, dest = line
    print(f'{num + 1:<4}{instruction:10}{source1 or "":10}{source2 or "":10}{dest or ""}')


with open(sys.argv[1], 'r') as f:
    [display(i, line) for i, line in enumerate(to_ir(analyze(parse(lex(f.read())))))]
