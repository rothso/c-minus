import lexer


class TestLexer(object):

    def test_reads_integers_surrounded_by_parentheses(self):
        assert lexer.lex("(123)") == [
            ('PUNCTUATION', '('),
            ('INTEGER', '123'),
            ('PUNCTUATION', ')')
        ]
