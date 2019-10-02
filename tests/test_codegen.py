import compiler.lexer as lexer
import compiler.parser as parser
import compiler.semantics as semantics
import compiler.codegen as codegen


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
            ('brle', '_t2', None, '21'),
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
          int x; int y;
          if (x > y) return(z+z); else x = 5;
        }
        void main(void) {
          int x; int y;
          y = sub(x);
        }
        ''') == [
            ('func', 'sub', 'int', '1'),
            ('param', None, None, 'z'),
            ('alloc', '4', None, 'z'),
            ('alloc', '4', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('comp', 'x', 'y', '_t0'),
            ('brle', '_t0', None, '11'),
            ('add', 'z', 'z', '_t1'),
            ('return', None, None, '_t1'),
            ('br', None, None, '12'),
            ('assign', '5', None, 'x'),
            ('end', 'func', 'sub', None),
            ('func', 'main', 'void', '0'),
            ('alloc', '4', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('arg', None, None, 'x'),
            ('call', 'sub', '1', '_t2'),
            ('assign', '_t2', None, 'y'),
            ('end', 'func', 'main', None),
        ]

    def test_sample_program_3(self):
        assert self.to_ir('''
        void main(void) {
           int x[10]; int y;
           y = (x[5] + 2) * y;
        }
        ''') == [
            ('func', 'main', 'void', '0'),
            ('alloc', '40', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('disp', 'x', '20', '_t0'),
            ('add', '_t0', '2', '_t1'),
            ('mult', '_t1', 'y', '_t2'),
            ('assign', '_t2', None, 'y'),
            ('end', 'func', 'main', None),
        ]

    def test_sample_quiz_10(self):
        assert self.to_ir('''
        int sub(int x) {
          int y;
          return (x + y);
        }
        void main(void) {
          int x[8]; int y; int z; int w;
          while (x[w] + y * z >= z * w) {
            int p;
            x[2] = p * z + w - p;
          }
          if (x[z] + 2 > y) y = x[0] * 5; else y = z - 1000;
          x[4] = sub(w);
        }
        ''') == [
            ('func', 'sub', 'int', '1'),
            ('param', None, None, 'x'),
            ('alloc', '4', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('add', 'x', 'y', '_t0'),
            ('return', None, None, '_t0'),
            ('end', 'func', 'sub', None),
            ('func', 'main', 'void', '0'),
            ('alloc', '32', None, 'x'),
            ('alloc', '4', None, 'y'),
            ('alloc', '4', None, 'z'),
            ('alloc', '4', None, 'w'),
            ('mult', 'w', '4', '_t1'),  # 13
            ('disp', 'x', '_t1', '_t2'),
            ('mult', 'y', 'z', '_t3'),
            ('add', '_t2', '_t3', '_t4'),
            ('mult', 'z', 'w', '_t5'),
            ('comp', '_t4', '_t5', '_t6'),
            ('brl', '_t6', None, '29'),
            ('block', None, None, None),
            ('alloc', '4', None, 'p'),
            ('mult', 'p', 'z', '_t7'),
            ('add', '_t7', 'w', '_t8'),
            ('sub', '_t8', 'p', '_t9'),
            ('disp', 'x', '8', '_t10'),
            ('assign', '_t9', None, '_t10'),
            ('end', 'block', None, None),
            ('br', None, None, '13'),
            ('mult', 'z', '4', '_t11'),  # 29
            ('disp', 'x', '_t11', '_t12'),
            ('add', '_t12', '2', '_t13'),
            ('comp', '_t13', 'y', '_t14'),
            ('brle', '_t14', None, '38'),
            ('disp', 'x', '0', '_t15'),
            ('mult', '_t15', '5', '_t16'),
            ('assign', '_t16', None, 'y'),
            ('br', None, None, '40'),
            ('sub', 'z', '1000', '_t17'),  # 38
            ('assign', '_t17', None, 'y'),
            ('arg', None, None, 'w'),  # 40
            ('call', 'sub', '1', '_t18'),
            ('disp', 'x', '16', '_t19'),
            ('assign', '_t18', None, '_t19'),
            ('end', 'func', 'main', None),
        ]
