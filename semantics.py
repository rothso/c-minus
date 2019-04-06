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
        self.functions = {}

    def insertVar(self, declaration: VarDeclaration):
        self.scope[declaration.name] = declaration

    def insertFun(self, declaration: FunDeclaration):
        self.functions[declaration.name] = declaration

    def lookup(self, name: str) -> Optional[VarDeclaration]:
        for scope in reversed(self.stack + [self.scope]):
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
            raise Exception("Not possible")

    def visit_var_declaration(self, declaration: VarDeclaration):
        self.insertVar(declaration)
        # Variable declarations can only use type specifier int and float
        if declaration.type not in [Type.INTEGER, Type.FLOAT]:
            raise ValueError(f'Declaration {declaration.name} cannot have void type')
        if declaration.array is not None:
            self.visit_array(declaration.array)

    def visit_fun_declaration(self, declaration: FunDeclaration):
        self.insertFun(declaration)

        # todo visit params

        # Functions not declared void must return values of the correct type
        has_return = self.visit_compound_statement(declaration.body, declaration.type)
        if declaration.type != Type.VOID and not has_return:
            raise ValueError(f'{declaration.type} function must have at least one return')

    def visit_compound_statement(self, statement: CompoundStatement, function_type: Type) -> bool:
        has_return = False
        self.add_scope()
        for var in statement.vars:
            self.visit_var_declaration(var)
        for statement in statement.body:
            has_return |= self.visit_statement(statement, function_type)
        self.remove_scope()
        return has_return

    def visit_statement(self, statement: Statement, function_type: Type) -> bool:
        if isinstance(statement, ExpressionStatement):
            if statement.expression is not None:
                self.visit_expression(statement.expression)
        if isinstance(statement, IfStatement):
            # Condition in an if statement must be an integer
            if self.visit_expression(statement.cond) != (Type.INTEGER, False):
                raise ValueError('The condition in an if statement must be an integer')
            has_return = self.visit_statement(statement.true, function_type)
            if statement.false is not None:
                has_return |= self.visit_statement(statement.false, function_type)
            return has_return
        elif isinstance(statement, ReturnStatement):
            exp = statement.expression
            kind, is_array = self.visit_expression(exp) if exp is not None else (Type.VOID, False)
            # Can only return simple structures (no arrays)
            if is_array:
                raise ValueError(f'An array cannot be returned from a function')
            # Return type must match function type
            if kind is not function_type:
                raise ValueError(f'Return type does not match function type {function_type}')
            return True
        return False

    # todo handle expression type
    def visit_expression(self, expression: Expression) -> (Type, bool):
        if isinstance(expression, BinaryOp):
            l_type, l_array = self.visit_expression(expression.lhs)
            r_type, r_array = self.visit_expression(expression.rhs)
            # Cannot perform binary operations on arrays
            if l_array or r_array:
                raise ValueError(f'Cannot perform {expression.op} on an array')
            # The left and right sides of the argument should be the same
            elif l_type is not r_type:
                raise ValueError('Mixed mode arithmetic is not supported')
            return l_type, False  # not an array

        elif isinstance(expression, Variable):
            variable = self.lookup(expression.name)
            # All variables must be declared in scope before they are used
            if variable is None:
                raise ValueError(f'Variable {expression.name} has not been defined')
            # Array indexes must be of type int
            if expression.index is not None:
                if self.visit_expression(expression.index) != (Type.INTEGER, False):
                    raise ValueError('Array indexes must be of type int')
                return variable.type, False  # not an array
            return variable.type, variable.is_array()  # raw variable

        elif isinstance(expression, Number):
            return Type.INTEGER if isinstance(expression.value, int) else Type.FLOAT, False
        raise Exception("Not implemented")

    @staticmethod
    def visit_array(array: Number):
        # Array indexes must be of type int
        if isinstance(array.value, float):
            raise ValueError(f'Invalid array size type: {array.value}')
