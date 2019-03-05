import lexer


class TestIntegers(object):

    def test_reads_integers_surrounded_by_parentheses(self):
        assert lexer.lex('(123)') == [
            ('PUNCTUATION', '('),
            ('INTEGER', '123'),
            ('PUNCTUATION', ')')
        ]


class TestFloats(object):

    # Basic floats
    def test_reads_floats_at_end_of_string(self):
        assert lexer.lex('123.12345') == [('FLOAT', '123.12345')]

    def test_doesnt_read_float_with_trailing_dot(self):
        assert lexer.lex('123.') == [('INTEGER', '123'), ('INVALID', '.')]

    def test_doesnt_read_float_without_leading_number(self):
        assert lexer.lex('.5') == [('INVALID', '.'), ('INTEGER', '5')]

    def test_skips_dangling_float_decimal(self):
        assert lexer.lex('1.)') == [('INTEGER', '1'), ('INVALID', '.'), ('PUNCTUATION', ')')]

    # Floats in scientific notation
    def test_reads_floats_in_scientific_notation(self):
        assert lexer.lex('1.2E2') == [('FLOAT', '1.2E2')]

    def test_reads_floats_in_signed_scientific_notation(self):
        assert lexer.lex('120.0E-2') == [('FLOAT', '120.0E-2')]

    def test_reads_integers_in_scientific_notation_as_floats(self):
        assert lexer.lex('1E2') == [('FLOAT', '1E2')]

    def test_doesnt_read_float_with_trailing_e(self):
        assert lexer.lex('4.0E') == [('FLOAT', '4.0'), ('INVALID', 'E')]

    def test_doesnt_read_e_as_float(self):
        assert lexer.lex('.E') == [('INVALID', '.'), ('INVALID', 'E')]

    def test_doesnt_read_incomplete_scientific_notation_as_float(self):
        assert lexer.lex('6.0E+') == [('FLOAT', '6.0'), ('INVALID', 'E'), ('OPERATOR', '+')]
