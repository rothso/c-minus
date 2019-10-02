import sys
from compiler.lexer import lex
from compiler.parser import parse
from compiler.semantics import analyze
from compiler.codegen import to_ir


def display(num, line):
    instruction, source1, source2, dest = line
    print(f'{num + 1:<4}{instruction:10}{source1 or "":10}{source2 or "":10}{dest or ""}')


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        [display(i, line) for i, line in enumerate(to_ir(analyze(parse(lex(f.read())))))]
