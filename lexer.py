import re

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
