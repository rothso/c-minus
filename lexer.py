import re


def strip_comments(string: str):
    s = ''
    depth = 0
    string += " "
    it = iter(range(len(string) - 1))
    for i in it:
        peek2 = string[i] + string[i + 1]
        if peek2 == '/*':
            depth += 1
            next(it)
        elif peek2 == '*/' and depth > 0:
            depth -= 1
            next(it)
        elif depth == 0:
            s += string[i]
    return s


scanner = re.Scanner([
    (r'\(', lambda _, token: ('PUNCTUATION', '(')),
    (r'\)', lambda _, token: ('PUNCTUATION', ')')),
    (r'\[', lambda _, token: ('PUNCTUATION', '[')),
    (r'\]', lambda _, token: ('PUNCTUATION', ']')),
    (r'\{', lambda _, token: ('PUNCTUATION', '{')),
    (r'\}', lambda _, token: ('PUNCTUATION', '}')),
    (r'\+', lambda _, token: ('OPERATOR', '+')),
    (r'(?=\d*[.eE]\d+)\d+(\.\d+)?([eE][+-]?\d+)?', lambda _, token: ('FLOAT', token)),
    (r'\d+', lambda _, token: ('INTEGER', token)),
    (r'int|float|void|while|if|else|return', lambda _, token: ('KEYWORD', token)),
    (r'[a-zA-Z]+', lambda _, token: ('IDENTIFIER', token)),
    (r'\s+', lambda _, token: None),  # ignore whitespace
    (r'.', lambda _, token: ('INVALID', token)),
])


def lex(string: str):
    results, remainder = scanner.scan(string)
    return results
