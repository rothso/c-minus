from dataclasses import dataclass
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


# Expression

class Expression:
    pass


@dataclass
class Variable(Expression):
    name: str
    index: Optional[Expression]


@dataclass
class Call(Expression):
    name: str
    args: List[Expression]


@dataclass
class BinaryOp(Expression):
    op: str
    lhs: Expression
    rhs: Expression


@dataclass
class AssignmentExpression(Expression):
    var: Variable
    value: Expression


@dataclass
class Number(Expression):
    value: Union[int, float]


# Statement

class Statement:
    pass


@dataclass
class ExpressionStatement(Statement):
    expression: Optional[Expression]


@dataclass
class ReturnStatement(Statement):
    expression: Optional[Expression]


@dataclass
class WhileStatement(Statement):
    cond: Expression
    body: Statement


@dataclass
class IfStatement(Statement):
    cond: Expression
    true: Statement
    false: Optional[Statement]


@dataclass
class Declaration:
    type: Type
    name: str


@dataclass
class VarDeclaration(Declaration):
    array: Optional[Number]


@dataclass
class CompoundStatement(Statement):
    vars: List[VarDeclaration]
    body: List[Statement]


@dataclass
class ParamFormal:
    type: Type
    name: str
    is_array: bool


@dataclass
class FunDeclaration(Declaration):
    params: List[ParamFormal]
    body: Optional[CompoundStatement]


@dataclass
class Program:
    declarations: List[Declaration]
