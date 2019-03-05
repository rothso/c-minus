import lexer


class TestLexer(object):

    def test_reads_integers_surrounded_by_parentheses(self):
        assert lexer.lex('(123)') == [
            ('PUNCTUATION', '('),
            ('INTEGER', '123'),
            ('PUNCTUATION', ')')
        ]

    def test_reads_floats_at_end_of_string(self):
        assert lexer.lex('123.12345') == [('FLOAT', '123.12345')]

    def test_doesnt_read_float_with_trailing_dot(self):
        assert lexer.lex('123.') == [('INTEGER', '123'), ('INVALID', '.')]

    def test_skips_dangling_float_decimal(self):
        assert lexer.lex('1.)') == [('INTEGER', '1'), ('INVALID', '.'), ('PUNCTUATION', ')')]
