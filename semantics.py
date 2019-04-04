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

        # The last declaration should be "void main(void)"
        d = program.declarations[-1]
        if not (isinstance(d, FunDeclaration) and d.type == Type.VOID and d.params is None):
            raise ValueError('Last declaration should be void main(void)')

    def visit_declaration(self, declaration: Declaration):
        if isinstance(declaration, VarDeclaration):
            self.scope[declaration.name] = declaration
            self.visit_var_declaration(declaration)
        elif isinstance(declaration, FunDeclaration):
            self.scope[declaration.name] = declaration
            self.visit_fun_declaration(declaration)
        else:
            raise Exception

    def visit_var_declaration(self, declaration: VarDeclaration):
        # Variable declarations can only use type specifier int and float
        if declaration.type not in [Type.INTEGER, Type.FLOAT]:
            raise ValueError(f'Declaration {declaration.name} cannot have void type')

        if declaration.array is not None:
            self.visit_array(declaration.array)

    def visit_fun_declaration(self, declaration: FunDeclaration):
        # todo visit params
        if declaration.body is not None:
            self.visit_compound_statement(declaration.body)

    def visit_compound_statement(self, statement: CompoundStatement):
        for var in statement.vars:
            self.visit_var_declaration(var)
        # todo visit statements

    @staticmethod
    def visit_array(array: Number):
        # Array indexes must be of type int
        if isinstance(array.value, float):
            raise ValueError(f'Invalid array size type: {array.value}')
