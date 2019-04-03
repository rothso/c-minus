from astnodes import *


def analyze(program: Optional[Program]) -> bool:
    try:
        if program is not None:
            SemanticAnalyzer().visit_program(program)
            return True
        else:
            return False
    except ValueError as e:
        print(str(e))
        return False


class SemanticAnalyzer:

    def __init__(self):
        self.scope = {}

    def visit_program(self, program: Program):
        for declaration in program.declarations:
            self.visit_declaration(declaration)
        # todo assert declaration list contains void main(void)

    def visit_declaration(self, declaration: Declaration):
        if isinstance(declaration, VarDeclaration):
            self.scope[declaration.name] = declaration
            if declaration.array is not None:
                self.visit_array(declaration.array)
        elif isinstance(declaration, FunDeclaration):
            self.scope[declaration.name] = declaration
        else:
            raise Exception

    @staticmethod
    def visit_array(array: Number):
        # Array indexes must be of type int
        if isinstance(array.value, float):
            raise ValueError(f'invalid array size: {array.value}')
