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
        return 'alloc', str(4 * (dec.array or Number(1)).value), None, dec.name

    def fun_declaration(self, dec: FunDeclaration) -> List[Quadruple]:
        func = ('func', dec.name, dec.type.to_string(), str(len(dec.params or [])))
        params = [('param', None, None, p.name) for p in dec.params or []]
        allocs = [('alloc', '4', None, p.name) for p in dec.params or []]
        body = self.compound_statement(dec.body)
        end = ('end', 'func', dec.name, None)
        return [func] + params + allocs + body + [end]

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
        elif isinstance(stmt, IfStatement):
            return self.if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.while_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.return_statement(stmt)

    def if_statement(self, stmt: IfStatement) -> List[Quadruple]:
        cond, variable = self.expression(stmt.cond)
        true = self.statement(stmt.true)
        false = self.statement(stmt.false) if stmt.false is not None else []
        jump_else = ('brle', variable, None, len(true) + 2)
        jump_end = ('br', None, None, len(false) + 1)
        return cond + [jump_else] + true + [jump_end] + false

    def while_statement(self, stmt: WhileStatement) -> List[Quadruple]:
        cond, variable = self.expression(stmt.cond)
        body = self.statement(stmt.body)
        jump = ('brleq', variable, None, len(body) + 2)
        br = ('br', None, None, -(len(body) + len(cond) + 1))
        return cond + [jump] + body + [br]

    def return_statement(self, stmt: ReturnStatement) -> List[Quadruple]:
        if stmt.expression is not None:
            rhs, variable = self.expression(stmt.expression)
            ret = ('return', None, None, variable)
            return rhs + [ret]
        else:
            ret = ('return', None, None, None)
            return [ret]

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
        elif isinstance(expr, Call):
            exprs = [self.expression(arg) for arg in expr.args]
            args = [('arg', None, None, var) for _, var in exprs]
            dest = self.next_temp()
            call = ('call', expr.name, str(len(args)), dest)
            return [q for quad, _ in exprs for q in quad] + args + [call], dest
        elif isinstance(expr, Variable):
            if expr.index is not None:
                index, variable = self.expression(expr.index)
                temp = self.next_temp()
                if variable.isdigit():
                    disp = ('disp', expr.name, str(int(variable) * 4), temp)
                    return index + [disp], temp
                else:
                    temp2 = self.next_temp()
                    mult = ('mult', variable, '4', temp)
                    disp = ('disp', expr.name, temp, temp2)
                    return index + [mult, disp], temp2
            return [], expr.name
        elif isinstance(expr, Number):
            return [], str(expr.value)
