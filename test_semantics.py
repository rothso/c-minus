import lexer
import parser
import semantics


class TestSemantics(object):

    @staticmethod
    def analyze(string: str):
        parse = parser.parse(lexer.lex(string))
        assert parse is not None  # make sure the program is grammatically valid
        return semantics.analyze(parse)

    @staticmethod
    def with_main(string: str) -> str:
        return string + '''
        void main(void) {}
        '''


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
        int y[10.0];
        void main(void) { int y[2.0]; }
        ''') is False

    def test_array_indexes_must_be_int(self):
        assert self.analyze('''
        int x[10];
        void main(void) { x[2 + 2]; }
        ''') is True

    def test_array_indexes_cannot_be_float(self):
        assert self.analyze('''
        int y[10];
        void main(void) { y[2.0 + 2.0]; }
        ''') is False


class TestReturns(TestSemantics):

    def test_int_function_cannot_return_float(self):
        assert self.analyze(self.with_main('''
        int f(void) { return 4.0E-13; }
        ''')) is False

    def test_int_function_cannot_empty_return(self):
        assert self.analyze(self.with_main('''
        int f(void) { return; }
        ''')) is False

    def test_float_function_cannot_return_int(self):
        assert self.analyze(self.with_main('''
        float f(void) { return 4; }
        ''')) is False

    def test_void_function_cannot_return_int(self):
        assert self.analyze('''
        void main(void) { return 4; }
        ''') is False

    def test_non_void_functions_must_return(self):
        assert self.analyze(self.with_main('''
        int f(void) { }
        ''')) is False

    def test_void_function_optionally_return(self):
        assert self.analyze('''
        void x(void) { }
        void main(void) { return; }
        ''') is True

    def test_multiple_returns_must_all_match_type(self):
        assert self.analyze(self.with_main('''
        int f(void) { if (1) return 4; else return 5; }
        ''')) is True

    def test_cannot_return_arrays(self):
        assert self.analyze(self.with_main('''
        int x[5];
        int f(void) { return x; }
        ''')) is False


class TestIterators(TestSemantics):

    def test_if_condition_can_be_int(self):
        assert self.analyze('''
        void main(void) { if (2) 2; }
        ''') is True

    def test_if_condition_cannot_be_float(self):
        assert self.analyze('''
        void main(void) { if (2.0) 2; }
        ''') is False


class TestExpression(TestSemantics):

    def test_int_plus_float_should_fail(self):
        assert self.analyze('''
        void main(void) { 2.0 + 2; }
        ''') is False

    def test_int_plus_int_should_pass(self):
        assert self.analyze('''
        void main(void) { 2 + 2; }
        ''') is True

    def test_cannot_add_arrays(self):
        assert self.analyze('''
        int x[20];
        void main(void) { x + x; }
        ''') is False

    def test_cannot_add_void_types(self):
        assert self.analyze('''
        void main(void) { main() + main(); }
        ''') is False


class TestTypes(TestSemantics):

    def test_variable_declaration_cannot_use_void(self):
        assert self.analyze('''
        void x;
        void main(void) { void y; }
        ''') is False

    def test_cannot_use_void_type_as_argument(self):
        assert self.analyze('''
        void main(void) { return main(); }
        ''') is False


class TestScope(TestSemantics):

    def test_cannot_call_undeclared_variables(self):
        assert self.analyze('''
        void main(void) { x + 2; }
        ''') is False

    def test_variables_in_current_scope_are_recognized(self):
        assert self.analyze('''
        void main(void) {
            int x;
            x + 2;
        }''')

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

    def test_shadowing_recognizes_closest_variable(self):
        assert self.analyze('''
        float x;
        void main(void) {
            int x;
            x + 4;
        }
        ''') is True

    def test_cannot_call_functions_before_they_are_declared(self):
        assert self.analyze('''
        void main(void) { f(); }
        ''') is False

    # todo cannot assign to out of scope variables
