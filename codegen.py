from typing import Tuple

from astnodes import *

Quadruple = Tuple[str, Optional[str], Optional[str], Union[Optional[str], int]]


def to_ir(program: Optional[Program]) -> List[Quadruple]:
    return [] if program is None else CodeGenerator().program(program)


class CodeGenerator:

    def __init__(self):
        self.ir: List[Quadruple] = []
        self.temp = -1  # temporary variable counter
        self.last_equality_op = None

    def next_temp(self) -> str:
        self.temp += 1
        return f'_t{self.temp}'

    def next_jump(self):
        jump = self.last_equality_op
        self.last_equality_op = None
        return {
            '>': 'brle',
            '<': 'brge',
            '>=': 'brl',
            '<=': 'brg',
            '==': 'brne',
            '!=': 'bre',
        }.get(jump)

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
        func = ('func', dec.name, dec.type.to_string(), str(len(dec.params)))
        params = [('param', None, None, p.name) for p in dec.params]
        allocs = [('alloc', '4', None, p.name) for p in dec.params]
        quads = self.compound_statement(dec.body)
        end = ('end', 'func', dec.name, None)
        return [func] + params + allocs + quads + [end]

    def compound_statement(self, stmt: CompoundStatement) -> List[Quadruple]:
        allocs = [self.var_declaration(dec) for dec in stmt.vars]
        quads = [quad for stmt in stmt.body for quad in self.statement(stmt)]
        return allocs + quads

    def statement(self, stmt: Statement) -> List[Quadruple]:
        if isinstance(stmt, ExpressionStatement):
            return self.expression(stmt.expression)[0] if stmt.expression is not None else []
        elif isinstance(stmt, CompoundStatement):
            block = ('block', None, None, None)
            end = ('end', 'block', None, None)
            return [block] + self.compound_statement(stmt) + [end]
        elif isinstance(stmt, IfStatement):
            return self.if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.while_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.return_statement(stmt)

    def _patch_comparison(self, expression: (List[Quadruple], str)) -> (List[Quadruple], str):
        # If the condition in an if/while does not use an equality op, compare the expression to 0
        cond, ref = expression
        if self.last_equality_op is None:
            ref2 = self.next_temp()
            self.last_equality_op = ">"
            return cond + [('comp', ref, '0', ref2)], ref2
        return expression

    def if_statement(self, stmt: IfStatement) -> List[Quadruple]:
        cond, ref = self._patch_comparison(self.expression(stmt.cond))
        jump = self.next_jump()
        true = self.statement(stmt.true)
        false = self.statement(stmt.false) if stmt.false is not None else []
        jump_else = (jump, ref, None, len(true) + 2)
        jump_end = ('br', None, None, len(false) + 1)
        return cond + [jump_else] + true + [jump_end] + false

    def while_statement(self, stmt: WhileStatement) -> List[Quadruple]:
        cond, ref = self._patch_comparison(self.expression(stmt.cond))
        jump = self.next_jump()
        quads = self.statement(stmt.body)
        jump_end = (jump, ref, None, len(quads) + 2)
        jump_loop = ('br', None, None, -(len(quads) + len(cond) + 1))
        return cond + [jump_end] + quads + [jump_loop]

    def return_statement(self, stmt: ReturnStatement) -> List[Quadruple]:
        if stmt.expression is not None:
            rhs, ref = self.expression(stmt.expression)
            return_fun = ('return', None, None, ref)
            return rhs + [return_fun]
        else:
            return_fun = ('return', None, None, None)
            return [return_fun]

    def expression(self, expr: Expression) -> (List[Quadruple], str):
        if isinstance(expr, BinaryOp):
            return self.binary_op(expr)
        elif isinstance(expr, AssignmentExpression):
            return self.assignment_expression(expr)
        elif isinstance(expr, Call):
            return self.call_expression(expr)
        elif isinstance(expr, Variable):
            return self.variable(expr)
        elif isinstance(expr, Number):
            return [], str(expr.value)

    def binary_op(self, expr) -> (List[Quadruple], str):
        mathops = {'+': 'add', '-': 'sub', '*': 'mult', '/': 'div'}
        lhs, lref = self.expression(expr.lhs)
        rhs, rref = self.expression(expr.rhs)
        ref = self.next_temp()
        is_mathop = expr.op in mathops
        op = (mathops[expr.op] if is_mathop else 'comp', lref, rref, ref)
        if not is_mathop:
            self.last_equality_op = expr.op
        return lhs + rhs + [op], ref

    def assignment_expression(self, expr) -> (List[Quadruple], str):
        rhs, rref = self.expression(expr.value)
        assign = [('assign', rref, None, expr.var.name)]
        return rhs + assign, expr.var.name

    def variable(self, expr) -> (List[Quadruple], str):
        if expr.index is not None:
            index, ref = self.expression(expr.index)
            dest = self.next_temp()
            if ref.isdigit():
                disp = ('disp', expr.name, str(int(ref) * 4), dest)
                return index + [disp], dest
            else:
                dest2 = self.next_temp()
                mult = ('mult', ref, '4', dest)
                disp = ('disp', expr.name, dest, dest2)
                return index + [mult, disp], dest2
        return [], expr.name

    def call_expression(self, expr) -> (List[Quadruple], str):
        quads = [self.expression(arg) for arg in expr.args]
        args = [('arg', None, None, var) for _, var in quads]
        ref = self.next_temp()
        call = ('call', expr.name, str(len(args)), ref)
        return [q for quad, _ in quads for q in quad] + args + [call], ref
