import lexer
import parser
import semantics
import codegen


class TestCodegen(object):

    @staticmethod
    def to_ir(string: str):
        analyzed = semantics.analyze(parser.parse(lexer.lex(string)))
        assert analyzed is not None  # make sure the program passes the semantic analysis
        return codegen.to_ir(analyzed)

    def test_sample_program_1(self):
        assert self.to_ir('''
        void main(void) {
          int x; int y; int z; int m;
          while(x + 3 * y > 5) {
            x = y + m / z;
            m = x - y + z * m / z;
          }
        }
        ''') == [
            ('func', 'main', 'void', '0'),
            ('alloc', '4', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('alloc', '4', None, 'z'),
            ('alloc', '4', None, 'm'),
            ('mult', '3', 'y', '_t0'),
            ('add', 'x', '_t0', '_t1'),
            ('comp', '_t1', '5', '_t2'),
            ('brleq', None, '_t2', '21'),
            ('block', None, None, None),
            ('div', 'm', 'z', '_t3'),
            ('add', 'y', '_t3', '_t4'),
            ('assign', '_t4', None, 'x'),
            ('sub', 'x', 'y', '_t5'),
            ('mult', 'z', 'm', '_t6'),
            ('div', '_t6', 'z', '_t7'),
            ('add', '_t5', '_t7', '_t8'),
            ('assign', '_t8', None, 'm'),
            ('end', 'block', None, None),
            ('br', None, None, '6'),
            ('end', 'func', 'main', None),
        ]

    def test_sample_program_2(self):
        assert self.to_ir('''
        int sub(int z) {
           if (x > y) return(z+z); else x = 5;
        }
        void main(void) {
          int x; int y;
          y = sub(x);
        }
        ''') == [
            ('func', 'sub', 'int', '1'),
            ('param', None, None, 'z'),
            ('alloc', 4, None, 'z'),
            ('comp', 'x', 'y', '_t0'),
            ('brle', '_t0', None, '10'),
            ('add', 'z', 'z', '_t1'),
            ('return', None, None, '_t1'),
            ('br', None, None, '11'),
            ('assign', None, '5', 'x'),
            ('end', 'func', 'sub', None),
            ('func', 'main', 'void', '0'),
            ('alloc', '4', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('arg', None, None, 'x'),
            ('call', 'sub', '1', '_t2'),
            ('assign', '_t2', None, 'y'),
            ('end', 'func', 'main', None),
        ]