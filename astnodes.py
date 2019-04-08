from enum import Enum
from typing import List, Union, Optional


class Type(Enum):
    INTEGER = 1
    FLOAT = 2
    VOID = 3

    @staticmethod
    def from_string(kind):
        return {
            'int': Type.INTEGER,
            'float': Type.FLOAT,
            'void': Type.VOID,
        }[kind]

    def to_string(self):
        return {
            'INTEGER': 'int',
            'FLOAT': 'float',
            'VOID': 'void',
        }[self.name]


# Expression

class Expression:
    pass


class Variable(Expression):
    def __init__(self, name: str, index: Optional[Expression]):
        self.name = name
        self.index = index


class Call(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args


class BinaryOp(Expression):
    def __init__(self, op: str, lhs: Expression, rhs: Expression):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs


class AssignmentExpression(Expression):
    def __init__(self, var: Variable, value: Expression):
        self.var = var
        self.value = value


class Number(Expression):
    def __init__(self, value: Union[int, float]):
        self.value = value


# Statement

class Statement:
    pass


class ExpressionStatement(Statement):
    def __init__(self, expression: Optional[Expression]):
        self.expression = expression


class ReturnStatement(Statement):
    def __init__(self, expression: Optional[Expression]):
        self.expression = expression


class WhileStatement(Statement):
    def __init__(self, cond: Expression, body: Statement):
        self.cond = cond
        self.body = body


class IfStatement(Statement):
    def __init__(self, cond: Expression, true: Statement, false: Optional[Statement]):
        self.cond = cond
        self.true = true
        self.false = false


class Declaration:
    def __init__(self, kind: Type, name: str):
        self.type = kind
        self.name = name


class VarDeclaration(Declaration):
    def __init__(self, kind: Type, name: str, array: Optional[Number]):
        super().__init__(kind, name)
        self.array = array

    def is_array(self):
        return self.array is not None


class CompoundStatement(Statement):
    def __init__(self, variables: List[VarDeclaration], body: List[Statement]):
        self.vars = variables
        self.body = body


class ParamFormal:
    def __init__(self, kind: Type, name: str, is_array: bool):
        self.type = kind
        self.name = name
        self.is_array = is_array


class FunDeclaration(Declaration):
    def __init__(self, kind: Type, name: str, params: Optional[List[ParamFormal]],
                 body: CompoundStatement):
        super().__init__(kind, name)
        self.params = params
        self.body = body


class Program:
    def __init__(self, declarations: List[Declaration]):
        self.declarations = declarations
