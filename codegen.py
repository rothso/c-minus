from typing import Tuple

from astnodes import *

Quadruple = Tuple[str, Optional[str], Optional[str], Union[Optional[str], int]]


def to_ir(program: Optional[Program]) -> List[Quadruple]:
    return [] if program is None else CodeGenerator().program(program)


class CodeGenerator:

    def __init__(self):
        self.ir: List[Quadruple] = []
        self.temp = -1  # temporary variable counter

    def next_temp(self) -> str:
        self.temp += 1
        return f'_t{self.temp}'

    def program(self, program: Program) -> List[Quadruple]:
        return [(q[0], q[1], q[2], str(q[3] + i + 1)) if q[0].startswith('br') else q for i, q in
                enumerate([q for d in program.declarations for q in self.declaration(d)])]

    def declaration(self, dec: Declaration) -> List[Quadruple]:
        if isinstance(dec, VarDeclaration):
            return [self.var_declaration(dec)]
        elif isinstance(dec, FunDeclaration):
            return self.fun_declaration(dec)
        else:
            raise Exception('Unknown declaration type')

    @staticmethod
    def var_declaration(dec: VarDeclaration) -> Quadruple:
        return 'alloc', '4' * (dec.array or 1), None, dec.name

    def fun_declaration(self, dec: FunDeclaration) -> List[Quadruple]:
        func = ('func', dec.name, dec.type.to_string(), str(len(dec.params or [])))
        # params = [('alloc', '4', None, p.name) for p in dec.params or []]
        params = []  # TODO
        body = self.compound_statement(dec.body)
        end = ('end', 'func', dec.name, None)
        return [func] + params + body + [end]

    def compound_statement(self, stmt: CompoundStatement) -> List[Quadruple]:
        variables = [self.var_declaration(dec) for dec in stmt.vars]
        body = [quad for stmt in stmt.body for quad in self.statement(stmt)]
        return variables + body

    def statement(self, stmt: Statement) -> List[Quadruple]:
        if isinstance(stmt, ExpressionStatement):
            return self.expression(stmt.expression)[0]
        elif isinstance(stmt, CompoundStatement):
            block_start = ('block', None, None, None)
            block_end = ('end', 'block', None, None)
            return [block_start] + self.compound_statement(stmt) + [block_end]
        elif isinstance(stmt, WhileStatement):
            return self.while_statement(stmt)

    def while_statement(self, stmt: WhileStatement) -> List[Quadruple]:
        cond, variable = self.expression(stmt.cond)
        body = self.statement(stmt.body)
        jump = ('brleq', None, variable, len(body) + 2)
        br = ('br', None, None, -(len(body) + len(cond) + 1))
        return cond + [jump] + body + [br]

    def expression(self, expr: Expression) -> (List[Quadruple], str):
        if isinstance(expr, BinaryOp):
            mathops = {'+': 'add', '-': 'sub', '*': 'mult', '/': 'div'}

            lhs, l_source = self.expression(expr.lhs)
            rhs, r_source = self.expression(expr.rhs)
            dest = self.next_temp()

            if expr.op in mathops.keys():
                quad = (mathops[expr.op], l_source, r_source, dest)
            else:
                quad = ('comp', l_source, r_source, dest)

            return lhs + rhs + [quad], dest
        elif isinstance(expr, AssignmentExpression):
            dest = expr.var.name
            rhs, r_source = self.expression(expr.value)
            return rhs + [('assign', r_source, None, dest)], dest
        elif isinstance(expr, Variable):
            return [], expr.name
        elif isinstance(expr, Number):
            return [], str(expr.value)
