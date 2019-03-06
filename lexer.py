import re

scanner = re.Scanner([
    (r'\s+', lambda _, token: None),  # ignore whitespace
    (r'//.*\n', lambda _, token: None),  # ignore line comment
    (r'\(', lambda _, token: ('PUNCTUATION', '(')),
    (r'\)', lambda _, token: ('PUNCTUATION', ')')),
    (r'\[', lambda _, token: ('PUNCTUATION', '[')),
    (r'\]', lambda _, token: ('PUNCTUATION', ']')),
    (r'\{', lambda _, token: ('PUNCTUATION', '{')),
    (r'\}', lambda _, token: ('PUNCTUATION', '}')),
    (r',', lambda _, token: ('PUNCTUATION', ',')),
    (r';', lambda _, token: ('PUNCTUATION', ';')),
    (r'==', lambda _, token: ('EQUALITYOP', '==')),
    (r'>=', lambda _, token: ('EQUALITYOP', '>=')),
    (r'<=', lambda _, token: ('EQUALITYOP', '<=')),
    (r'>', lambda _, token: ('EQUALITYOP', '>')),
    (r'<', lambda _, token: ('EQUALITYOP', '<')),
    (r'\+', lambda _, token: ('MATHOP', '+')),
    (r'\-', lambda _, token: ('MATHOP', '-')),
    (r'/', lambda _, token: ('MATHOP', '/')),
    (r'\*', lambda _, token: ('MATHOP', '*')),
    (r'=', lambda _, token: ('OPERATOR', '=')),
    (r'(?=\d*[.eE]\d+)\d+(\.\d+)?([eE][+-]?\d+)?', lambda _, token: ('FLOAT', token)),
    (r'\d+', lambda _, token: ('INTEGER', token)),
    (r'int|float|void|while|if|else|return', lambda _, token: ('KEYWORD', token)),
    (r'[a-zA-Z]+', lambda _, token: ('IDENTIFIER', token)),
    (r'.', lambda _, token: ('INVALID', token)),
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
    results, remainder = scanner.scan(strip_comments(string))
    return results
