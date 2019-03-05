import re

scanner = re.Scanner([
    (r'\(', lambda _, token: ('PUNCTUATION', '(')),
    (r'\)', lambda _, token: ('PUNCTUATION', ')')),
    (r'[0-9]+', lambda _, token: ('INTEGER', token))
])


def lex(string: str):
    results, remainder = scanner.scan(string)
    return results
