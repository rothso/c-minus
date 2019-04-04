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
        self.stack = []
        self.scope = {}

    def insert(self, declaration: Declaration):
        self.scope[declaration.name] = declaration

    def lookup(self, name: str):
        for scope in reversed(self.stack):
            declaration = scope.get(name)
            if declaration is not None:
                return declaration
        return None

    def add_scope(self):
        self.stack.append(self.scope)
        self.scope = {}

    def remove_scope(self):
        self.scope = self.stack.pop()

    def visit_program(self, program: Program):
        for declaration in program.declarations:
            self.visit_declaration(declaration)

        # The last declaration should be "void main(void)"
        d = program.declarations[-1]
        if not (isinstance(d, FunDeclaration) and d.type == Type.VOID and d.params is None):
            raise ValueError('Last declaration should be void main(void)')

    def visit_declaration(self, declaration: Declaration):
        if isinstance(declaration, VarDeclaration):
            self.visit_var_declaration(declaration)
        elif isinstance(declaration, FunDeclaration):
            self.visit_fun_declaration(declaration)
        else:
            raise Exception

    def visit_var_declaration(self, declaration: VarDeclaration):
        self.insert(declaration)

        # Variable declarations can only use type specifier int and float
        if declaration.type not in [Type.INTEGER, Type.FLOAT]:
            raise ValueError(f'Declaration {declaration.name} cannot have void type')

        if declaration.array is not None:
            self.visit_array(declaration.array)

    def visit_fun_declaration(self, declaration: FunDeclaration):
        self.insert(declaration)

        # todo visit params
        if declaration.body is not None:
            self.visit_compound_statement(declaration.body)

    def visit_compound_statement(self, statement: CompoundStatement):
        self.add_scope()
        for var in statement.vars:
            self.visit_var_declaration(var)
        for statement in statement.body:
            self.visit_statement(statement)
        self.remove_scope()

    def visit_statement(self, statement: Statement):
        if isinstance(statement, ExpressionStatement):
            if statement.expression is not None:
                self.visit_expression(statement.expression)

    # todo handle expression type
    def visit_expression(self, expression: Expression):
        if isinstance(expression, BinaryOp):
            # todo verify operator-operand agreement
            self.visit_expression(expression.lhs)
            self.visit_expression(expression.rhs)
        elif isinstance(expression, Variable):
            # All variables must be declared in scope before they are used
            if self.lookup(expression.name) is None:
                raise ValueError(f'Variable {expression.name} has not been defined')
            # todo verify index is a number

    @staticmethod
    def visit_array(array: Number):
        # Array indexes must be of type int
        if isinstance(array.value, float):
            raise ValueError(f'Invalid array size type: {array.value}')
