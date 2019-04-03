import lexer
import parser
import semantics


class TestSemantics(object):

    @staticmethod
    def analyze(string: str):
        return semantics.analyze(parser.parse(lexer.lex(string)))


class TestArrays(TestSemantics):

    def test_array_declaration_size_must_be_int(self):
        assert self.analyze('int x[1];') is True

    def test_array_declaration_size_cannot_be_float(self):
        assert self.analyze('int x[1.1];') is False
