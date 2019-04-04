import lexer
import parser
import semantics


class TestSemantics(object):

    @staticmethod
    def analyze(string: str):
        parse = parser.parse(lexer.lex(string))
        assert parse is not None  # make sure the program is grammatically valid
        return semantics.analyze(parse)


class TestProgram(TestSemantics):

    def test_last_declaration_should_be_void_main_void(self):
        assert self.analyze('''void main(void) { }''') is True
        assert self.analyze('''int main(void) { }''') is False
        assert self.analyze('''int f(void) { }''') is False


class TestArrays(TestSemantics):

    def test_array_declaration_size_must_be_int(self):
        assert self.analyze('''
        int x[10];
        void main(void) { int x[2]; }
        ''') is True

    def test_array_declaration_size_cannot_be_float(self):
        assert self.analyze('''
        int y[10];
        void main(void) { int y[2.0]; }
        ''') is False
