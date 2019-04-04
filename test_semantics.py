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


class TestTypes(TestSemantics):

    def test_variable_declaration_cannot_use_void(self):
        assert self.analyze('''
        void x;
        void main(void) {
          void y;
        }''') is False


class TestScope(TestSemantics):

    def test_cannot_call_undeclared_variables(self):
        assert self.analyze('''
        void main(void) { x + 2; }
        ''') is False

    def test_variables_in_outer_scope_are_recognized(self):
        assert self.analyze('''
        int x;
        void main(void) { x + 2; }
        ''') is True

    def test_cannot_call_out_of_scope_variables(self):
        assert self.analyze('''
        void f(void) { int x; }
        void main(void) {
          x + 4;
        }''') is False

    # todo cannot assign to out of scope variables
