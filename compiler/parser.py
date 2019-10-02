from typing import Callable

from .astnodes import *
from .lexer import Token


def parse(tokens: List[Token]) -> Optional[Program]:
    parser = CMinusParser(tokens)
    try:
        return parser.parse()
    except:
        return None


class CMinusParser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def match(self, matcher: Callable[[Token], str], *params: str) -> List[str]:
        values = []
        for x in params:
            head = self.tokens.pop(0)
            if matcher(head) != x:
                raise Exception('unexpected token', head)
            values.append(head.val)
        return values

    def accept_type(self, *types: str) -> List[str]:
        return self.match(lambda token: token.type, *types)

    def accept_val(self, *values: str) -> List[str]:
        return self.match(lambda token: token.val, *values)

    def union(self, options: List[str]) -> str:
        for option in options:
            if self.next().val == option:
                self.accept_val(option)
                return option
        raise Exception('unexpected token', self.next())

    def next(self) -> Token:
        return self.tokens[0]

    def parse(self) -> Program:
        program = self.program()
        if self.tokens:
            raise Exception('unexpected tokens after declaration list', self.tokens)
        return program

    # program -> declaration declaration-list
    def program(self) -> Program:
        return Program(self.declaration_list([self.declaration()]))

    # declaration-list -> declaration declaration-list | ϵ
    def declaration_list(self, declarations: List[Declaration]) -> List[Declaration]:
        try:
            if self.next().val in ['int', 'float', 'void']:
                return self.declaration_list(declarations + [self.declaration()])
        except IndexError:
            return declarations  # end of program

    # declaration -> type-specifier ID var-declaration ; | type-specifier ID ( params ) compound-stmt
    def declaration(self) -> Declaration:
        kind = self.type_specifier()
        name = self.id()
        if self.next().val in ['[', ';']:
            array = self.var_declaration()
            self.accept_val(';')
            return VarDeclaration(kind, name, array)
        else:
            self.accept_val('(')
            params = self.params()
            self.accept_val(')')
            body = self.compound_stmt()
            return FunDeclaration(kind, name, params, body)

    # var-declaration -> [ NUM ] | ϵ
    def var_declaration(self) -> Optional[Number]:
        if self.next().val == '[':
            self.accept_val('[')
            number = self.number()
            self.accept_val(']')
            return number
        return None

    # identifier -> ID
    def id(self) -> str:
        return self.accept_type('ID')[0]

    # number -> INTEGER | FLOAT
    def number(self) -> Number:
        if self.next().type == 'INTEGER':
            return Number(int(self.accept_type('INTEGER')[0]))
        else:
            return Number(float(self.accept_type('FLOAT')[0]))

    # type-specifier -> int | float | void
    def type_specifier(self) -> Type:
        return Type.from_string(self.union(['int', 'float', 'void']))

    # params -> int ID param' param-list | float ID param' param-list | void ID param' param-list | void
    def params(self) -> List[ParamFormal]:
        if self.next().val in ['int', 'float']:
            return self.param_list([self.param()])
        else:
            self.accept_val('void')
            if self.next().type == 'ID':
                param = ParamFormal(Type.VOID, self.id(), self.param_())
                return self.param_list([param])
            return []

    # param-list' -> , param param-list | ϵ
    def param_list(self, params: List[ParamFormal]) -> List[ParamFormal]:
        if self.next().val == ',':
            self.accept_val(',')
            return self.param_list(params + [self.param()])
        return params

    # param -> type-specifier ID param'
    def param(self) -> ParamFormal:
        kind = self.type_specifier()
        name = self.id()
        is_array = self.param_()
        return ParamFormal(kind, name, is_array)

    # param' -> [] | ϵ
    def param_(self) -> bool:
        if self.next().val == '[':
            self.accept_val('[', ']')
            return True
        return False

    # compound-stmt -> { local-declarations statement-list }
    def compound_stmt(self) -> CompoundStatement:
        self.accept_val('{')
        decls = self.local_declarations([])
        body = self.statement_list([])
        self.accept_val('}')
        return CompoundStatement(decls, body)

    # local-declarations -> type-specifier ID var-declaration ; local-declarations | ϵ
    def local_declarations(self, decls: List[VarDeclaration]) -> List[VarDeclaration]:
        if self.next().val in ['int', 'float', 'void']:
            kind = self.type_specifier()
            name = self.id()
            array = self.var_declaration()
            self.accept_val(';')
            return self.local_declarations(decls + [VarDeclaration(kind, name, array)])
        return decls

    # statement-list -> statement statement-list | ϵ
    def statement_list(self, statements: List[Statement]) -> List[Statement]:
        if self.next().val in ['(', ';', 'if', 'return', 'while', '{'] or (
                self.next().type in ['ID', 'INTEGER', 'FLOAT']):
            return self.statement_list(statements + [self.statement()])
        return statements

    # statement -> expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
    def statement(self) -> Statement:
        if self.next().val in ['(', ';'] or self.next().type in ['ID', 'INTEGER', 'FLOAT']:
            return self.expression_stmt()
        elif self.next().val == '{':
            return self.compound_stmt()
        elif self.next().val == 'if':
            return self.selection_stmt()
        elif self.next().val == 'while':
            return self.iteration_stmt()
        else:
            return self.return_stmt()

    # expression-stmt -> expression ; | ;
    def expression_stmt(self) -> ExpressionStatement:
        if self.next().val == '(' or self.next().type in ['ID', 'INTEGER', 'FLOAT']:
            expression = self.expression()
        else:
            expression = None
        self.accept_val(';')
        return ExpressionStatement(expression)

    # selection-stmt -> if ( expression ) statement selection-stmt'
    def selection_stmt(self) -> IfStatement:
        self.accept_val('if', '(')
        cond = self.expression()
        self.accept_val(')')
        true = self.statement()
        false = self.selection_stmt_()
        return IfStatement(cond, true, false)

    # selection-stmt' -> else statement | ϵ
    def selection_stmt_(self) -> Optional[Statement]:
        if self.next().val == 'else':
            self.accept_val('else')
            return self.statement()
        return None

    # iteration-stmt -> while ( expression ) statement
    def iteration_stmt(self) -> WhileStatement:
        self.accept_val('while', '(')
        cond = self.expression()
        self.accept_val(')')
        body = self.statement()
        return WhileStatement(cond, body)

    # return-stmt -> return return-stmt' ;
    def return_stmt(self) -> ReturnStatement:
        self.accept_val('return')
        expression = self.return_stmt_()
        self.accept_val(';')
        return ReturnStatement(expression)

    # return-stmt' -> expression | ϵ
    def return_stmt_(self) -> Optional[Expression]:
        if self.next().val == '(' or self.next().type in ['ID', 'INTEGER', 'FLOAT']:
            return self.expression()
        return None

    # expression -> ID var' expression'' | ID ( args ) expression''' | ( expression ) expression''' | NUM expression'''
    def expression(self) -> Expression:
        if self.next().type == 'ID':
            name = self.id()
            if self.next().val == '(':
                self.accept_val('(')
                args = self.args()
                self.accept_val(')')
                return self.expression___(Call(name, args))
            else:
                index = self.var_()
                return self.expression__(Variable(name, index))
        else:
            if self.next().val == '(':
                self.accept_val('(')
                lhs = self.expression()
                self.accept_val(')')
                return self.expression___(lhs)
            else:
                lhs = self.number()
                return self.expression___(lhs)

    # expression'' -> = expression | expression'''
    def expression__(self, var: Variable) -> Expression:
        if self.next().val == '=':
            self.accept_val('=')
            return AssignmentExpression(var, self.expression())
        else:
            return self.expression___(var)

    # expression''' -> term' additive-expression' simple-expression
    def expression___(self, lhs: Expression) -> Expression:
        lhs = self.term_(lhs)
        lhs = self.additive_expression_(lhs)
        return self.simple_expression(lhs)

    # var -> ID var'
    def var(self) -> Variable:
        return Variable(self.id(), self.var_())

    # var' -> [ expression ] | ϵ
    def var_(self) -> Optional[Expression]:
        if self.next().val == '[':
            self.accept_val('[')
            expression = self.expression()
            self.accept_val(']')
            return expression
        return None

    # simple-expression -> relop additive-expression | ϵ
    def simple_expression(self, lhs: Expression) -> Expression:
        if self.next().type == 'RELOP':
            op = self.relop()
            rhs = self.additive_expression()
            return BinaryOp(op, lhs, rhs)
        return lhs

    # relop -> <= | < | > | >= | == | !=
    def relop(self) -> str:
        return self.union(['<=', '<', '>', '>=', '==', '!='])

    # additive-expression -> term additive-expression'
    def additive_expression(self) -> Expression:
        return self.additive_expression_(self.term())

    # additive-expression' -> addop term additive-expression' | ϵ
    def additive_expression_(self, lhs: Expression) -> Expression:
        if self.next().val in ['+', '-']:
            op = self.addop()
            rhs = self.term()
            node = BinaryOp(op, lhs, rhs)
            return self.additive_expression_(node)
        return lhs

    # addop -> + | -
    def addop(self) -> str:
        return self.union(['+', '-'])

    # term -> factor term'
    def term(self) -> Expression:
        return self.term_(self.factor())

    # term' -> mulop factor term' | ϵ
    def term_(self, lhs: Expression) -> Expression:
        if self.next().val in ['*', '/']:
            op = self.mulop()
            rhs = self.factor()
            node = BinaryOp(op, lhs, rhs)
            return self.term_(node)
        return lhs

    # mulop -> * | /
    def mulop(self) -> str:
        return self.union(['*', '/'])

    # factor -> ( expression ) | ID ( args ) | ID var' | NUM
    def factor(self) -> Expression:
        if self.next().val == '(':
            self.accept_val('(')
            expression = self.expression()
            self.accept_val(')')
            return expression
        elif self.next().type == 'ID':
            name = self.id()
            if self.next().val == '(':
                self.accept_val('(')
                args = self.args()
                self.accept_val(')')
                return Call(name, args)
            else:
                index = self.var_()
                return Variable(name, index)
        else:
            return self.number()

    # call -> ID ( args )
    def call(self) -> Call:
        name = self.id()
        self.accept_val('(')
        args = self.args()
        self.accept_val(')')
        return Call(name, args)

    # args -> expression arg-list' | ϵ
    def args(self) -> List[Expression]:
        if self.next().val == '(' or self.next().type in ['ID', 'INTEGER', 'FLOAT']:
            return self.arg_list([self.expression()])
        return []

    # arg-list' -> , expression arg-list' | ϵ
    def arg_list(self, expressions: List[Expression]) -> List[Expression]:
        if self.next().val == ',':
            self.accept_val(',')
            return self.arg_list(expressions + [self.expression()])
        return expressions
