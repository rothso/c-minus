import lexer
import parser
from astnodes import Program


class TestParser(object):

    @staticmethod
    def parse(string: str) -> bool:
        return isinstance(parser.parse(lexer.lex(string)), Program)

    # Regression tests
    def test_doesnt_accept_empty_variable_assignment(self):
        assert self.parse('''
        int main(void) {
            int x;
            x = ;
        }
        ''') is False

    def test_doesnt_accept_empty_parameter_list(self):
        assert self.parse('''
        int main() {
        }
        ''') is False

    def test_doesnt_accept_extra_tokens(self):
        assert self.parse('''
        void main(void) {
            while (true) {
                that = 10;
            }
        }
        extra
        ''') is False
