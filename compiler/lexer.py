import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'val'])
scanner = re.Scanner([
    (r'\s+', lambda _, tok: None),  # ignore whitespace
    (r'//.*\n', lambda _, tok: None),  # ignore line comment
    (r'==|>=|<=|>|<|!=', lambda _, token: Token('RELOP', token)),
    (r'\(|\)|\[|\]|\{|\}|,|;|=', lambda _, token: Token('PUNCTUATION', token)),
    (r'\+|-|/|\*', lambda _, token: Token('MATHOP', token)),
    (r'(?=\d*[.eE][+-]?\d+)\d+(\.\d+)?([eE][+-]?\d+)?', lambda _, token: Token('FLOAT', token)),
    (r'\d+', lambda _, token: Token('INTEGER', token)),
    (r'int|float|void|while|if|else|return', lambda _, token: Token('KEYWORD', token)),
    (r'[a-zA-Z]+', lambda _, token: Token('ID', token)),
    (r'.', lambda _, token: Token('INVALID', token)),
])


def strip_comments(string: str):
    string += " "
    s, depth = '', 0
    it = iter(range(len(string) - 1))
    for i in it:
        if string[i] + string[i + 1] == '/*':
            depth += 1
            next(it)
        elif string[i] + string[i + 1] == '*/' and depth > 0:
            depth -= 1
            next(it)
        elif depth == 0:
            s += string[i]
    return s


def lex(string: str):
    return scanner.scan(strip_comments(string))[0]
