from typing import Dict

from astnodes import *


def analyze(program: Optional[Program]) -> Optional[Program]:
    try:
        if program is not None:
            SemanticAnalyzer().visit_program(program)
    except ValueError:
        return None
    return program


class SemanticAnalyzer:

    def __init__(self):
        self.stack: List[Dict[str, ParamFormal]] = []
        self.scope: Dict[str, ParamFormal] = {}
        self.functions: Dict[str, FunDeclaration] = {}
        self.queue: List[ParamFormal] = []

    def insert_var(self, declaration: ParamFormal):
        # All variables may be declared only once per scope
        if declaration.name in self.scope:
            raise ValueError(f'Variable {declaration.name} has already been declared')
        self.scope[declaration.name] = declaration

    def insert_fun(self, declaration: FunDeclaration):
        # All variables may be declared only once
        if declaration.name in self.functions:
            raise ValueError(f'Function {declaration.name} has already been declared')

        self.functions[declaration.name] = declaration

    def lookup_var(self, name: str) -> Optional[ParamFormal]:
        for scope in reversed(self.stack + [self.scope]):
            declaration = scope.get(name)
            if declaration is not None:
                return declaration
        return None

    def lookup_fun(self, name: str) -> Optional[FunDeclaration]:
        return self.functions.get(name)

    def queue_var(self, declaration: ParamFormal):
        self.queue.append(declaration)

    def add_scope(self):
        self.stack.append(self.scope)
        self.scope = {}

        # Add any variable declarations that were queued
        for var in self.queue:
            self.insert_var(var)
        self.queue = []

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
            raise Exception('Unknown declaration type')

    def visit_var_declaration(self, declaration: VarDeclaration):
        self.insert_var(ParamFormal(declaration.type, declaration.name, declaration.is_array()))

        # Variable declarations can only use type specifier int and float
        if declaration.type not in [Type.INTEGER, Type.FLOAT]:
            raise ValueError(f'Declaration {declaration.name} cannot have void type')
        if declaration.array is not None:
            self.visit_array(declaration.array)

    def visit_fun_declaration(self, declaration: FunDeclaration):
        self.insert_fun(declaration)
        for param in declaration.params or []:
            self.visit_param(param)

        # Functions not declared void must return values of the correct type
        has_return = self.visit_compound_statement(declaration.body, declaration.type)
        if declaration.type != Type.VOID and not has_return:
            raise ValueError(f'{declaration.type} function must have at least one return')

    def visit_param(self, param: ParamFormal):
        self.queue_var(param)
        # Parameter types can only be int or float
        if param.type == Type.VOID:
            raise ValueError(f'Named parameter {param.name} cannot be of type void')

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
            return False
        elif isinstance(statement, CompoundStatement):
            return self.visit_compound_statement(statement, function_type)
        elif isinstance(statement, IfStatement):
            # Condition in an if statement must be an integer
            if self.visit_expression(statement.cond) != (Type.INTEGER, False):
                raise ValueError('The condition in an if statement must be an integer')
            has_return = self.visit_statement(statement.true, function_type)
            if statement.false is not None:
                has_return |= self.visit_statement(statement.false, function_type)
            return has_return
        elif isinstance(statement, WhileStatement):
            # Condition in a while statement must be an integer
            if self.visit_expression(statement.cond) != (Type.INTEGER, False):
                raise ValueError('The condition in a while statement must be an integer')
            return self.visit_statement(statement.body, function_type)
        elif isinstance(statement, ReturnStatement):
            kind = Type.VOID
            if statement.expression is not None:
                kind, is_array = self.visit_expression(statement.expression)
                # Can only return simple structures (no arrays)
                if is_array:
                    raise ValueError(f'An array cannot be returned from a function')
                # Cannot use void in a return expression
                if kind == Type.VOID:
                    raise ValueError(f'A void function cannot be used in a return expression')
            # Return type must match function type
            if kind is not function_type:
                raise ValueError(f'Return type does not match function type {function_type}')
            return True
        raise Exception('Unknown statement type')

    # todo handle expression type
    def visit_expression(self, expr: Expression) -> (Type, bool):
        if isinstance(expr, BinaryOp):
            l_type, l_array = self.visit_expression(expr.lhs)
            r_type, r_array = self.visit_expression(expr.rhs)
            # Cannot perform binary operations on arrays
            if l_array or r_array:
                raise ValueError(f'Cannot perform {expr.op} on an array')
            # Cannot use void in an arithmetic expression
            if l_type == Type.VOID or r_type == Type.VOID:
                raise ValueError(f'Cannot use void types in an arithmetic expression')
            # The left and right sides of the argument should be the same
            elif l_type is not r_type:
                raise ValueError('Mixed mode arithmetic is not supported')
            if expr.op in ['<=', '<', '>', '>=', '==', '!=']:
                return Type.INTEGER, False  # booleans are ints
            else:
                return l_type, False  # not an array
        elif isinstance(expr, AssignmentExpression):
            l_type, l_array = self.visit_variable(expr.var)
            r_type, r_array = self.visit_expression(expr.value)
            # Cannot perform binary operations on arrays
            if l_array or r_array:
                raise ValueError(f'Cannot perform assignment on an array')
            # The left and right sides of the argument should be the same
            elif l_type is not r_type:
                raise ValueError(f'Cannot assign an {r_type} to an {l_type}')
            return l_type, False  # not an arrays
        elif isinstance(expr, Variable):
            return self.visit_variable(expr)
        elif isinstance(expr, Call):
            function = self.lookup_fun(expr.name)
            # Functions must be declared before they are used
            if function is None:
                raise ValueError(f'Function {expr.name} has not been defined')
            # Function parameters and arguments must agree in number and type
            expected = [(p.type, p.is_array) for p in function.params or []]
            actual = [self.visit_expression(e) for e in expr.args]
            if expected != actual:
                raise ValueError(f'Parameter mismatch when calling function {expr.name}')
            return function.type, False
        elif isinstance(expr, Number):
            return Type.INTEGER if isinstance(expr.value, int) else Type.FLOAT, False
        raise Exception('Unknown expression type')

    def visit_variable(self, var: Variable) -> (Type, bool):
        variable = self.lookup_var(var.name)
        # All variables must be declared in scope before they are used
        if variable is None:
            raise ValueError(f'Variable {var.name} has not been defined')
        # Array indexes must be of type int
        if var.index is not None:
            if self.visit_expression(var.index) != (Type.INTEGER, False):
                raise ValueError('Array indexes must be of type int')
            return variable.type, False  # not an array
        return variable.type, variable.is_array  # raw variable

    @staticmethod
    def visit_array(array: Number):
        # Array indexes must be of type int
        if isinstance(array.value, float):
            raise ValueError(f'Invalid array size type: {array.value}')
