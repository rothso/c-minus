from typing import List, Callable

from lexer import Token


def parse(tokens: List[Token]) -> bool:
    parser = CMinusParser(tokens)
    try:
        parser.parse()
        return True
    except:
        return False


class CMinusParser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def match(self, matcher: Callable[[Token], str], *params: str):
        for x in params:
            head = self.tokens.pop(0)
            if matcher(head) != x:
                raise Exception('unexpected token', head)

    def accept_type(self, *types: str):
        self.match(lambda token: token.type, *types)

    def accept_val(self, *values: str):
        self.match(lambda token: token.val, *values)

    def union(self, options: List[str]):
        for option in options:
            if self.next().val == option:
                self.accept_val(option)
                return
        raise Exception("Parse error")

    def next(self) -> Token:
        return self.tokens[0]

    def parse(self):
        self.program()

    # program -> declaration-list
    def program(self):
        self.declaration_list()

    # declaration-list -> declaration declaration-list'
    def declaration_list(self):
        self.declaration()
        self.declaration_list_()

    # declaration-list' -> declaration declaration-list' | ϵ
    def declaration_list_(self):
        try:
            if self.next().val in ['int', 'float', 'void']:
                self.declaration()
                self.declaration_list_()
        except IndexError:
            return  # end of program

    # declaration -> type-specifier ID declaration'
    def declaration(self):
        self.type_specifier()
        self.accept_type('IDENTIFIER')
        self.declaration_()

    # declaration' -> var-declaration' ; | ( params ) compound-stmt
    def declaration_(self):
        if self.next().val in ['[', ';']:
            self.var_declaration_()
            self.accept_val(';')
        elif self.next().val == '(':
            self.accept_val('(')
            self.params()
            self.accept_val(')')
            self.compound_stmt()
        else:
            raise Exception("Parse error")

    # var-declaration' -> [ NUM ] | ϵ
    def var_declaration_(self):
        if self.next().val == '[':
            self.accept_val('[')
            self.number()
            self.accept_val(']')

    # number -> INTEGER | FLOAT
    def number(self):
        if self.next().type == 'INTEGER':
            self.accept_type('INTEGER')
        else:
            self.accept_type('FLOAT')

    # type-specifier -> int | float | void
    def type_specifier(self):
        self.union(['int', 'float', 'void'])

    # params -> int ID param' param-list' | float ID param' param-list' | void params'
    def params(self):
        if self.next().val in ['int', 'float']:
            self.accept_val(self.next().val)
            self.accept_type('IDENTIFIER')
            self.param_()
            self.param_list_()
        elif self.next().val == 'void':
            self.accept_val('void')
            self.params_()

    # params' -> ID param' param-list' | ϵ
    def params_(self):
        if self.next().type == 'IDENTIFIER':
            self.accept_type('IDENTIFIER')
            self.param_()
            self.param_list_()

    # param-list' -> , param param-list' | ϵ
    def param_list_(self):
        if self.next().val == ',':
            self.accept_val(',')
            self.param()
            self.param_list_()

    # param -> type-specifier ID param'
    def param(self):
        self.type_specifier()
        self.accept_type('IDENTIFIER')
        self.param_()

    # param' -> [] | ϵ
    def param_(self):
        if self.next().val == '[':
            self.accept_val('[')
            self.accept_val(']')

    # compound-stmt -> { local-declarations statement-list }
    def compound_stmt(self):
        self.accept_val('{')
        self.local_declarations()
        self.statement_list()
        self.accept_val('}')

    # local-declarations -> local-declarations'
    def local_declarations(self):
        self.local_declarations_()

    # local-declarations' -> type-specifier ID var-declaration' ; local-declarations' | ϵ
    def local_declarations_(self):
        if self.next().val in ['int', 'float', 'void']:
            self.type_specifier()
            self.accept_type('IDENTIFIER')
            self.var_declaration_()
            self.accept_val(';')
            self.local_declarations_()

    # statement-list -> statement-list'
    def statement_list(self):
        self.statement_list_()

    # statement-list' -> statement statement-list' | ϵ
    def statement_list_(self):
        if self.next().val in ['(', ';', 'if', 'return', 'while', '{'] or (
                self.next().type in ['IDENTIFIER', 'INTEGER', 'FLOAT']):
            self.statement()
            self.statement_list_()

    # statement -> expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
    def statement(self):
        if self.next().val in ['(', ';'] or self.next().type in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression_stmt()
        elif self.next().val == '{':
            self.compound_stmt()
        elif self.next().val == 'if':
            self.selection_stmt()
        elif self.next().val == 'while':
            self.iteration_stmt()
        elif self.next().val == 'return':
            self.return_stmt()

    # expression-stmt -> expression ; | ;
    def expression_stmt(self):
        if self.next().val == '(' or self.next().type in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression()
        self.accept_val(';')

    # selection-stmt -> if ( expression ) statement selection-stmt'
    def selection_stmt(self):
        self.accept_val('if')
        self.accept_val('(')
        self.expression()
        self.accept_val(')')
        self.statement()
        self.selection_stmt_()

    # selection-stmt' -> else statement | ϵ
    def selection_stmt_(self):
        if self.next().val == 'else':
            self.accept_val('else')
            self.statement()

    # iteration-stmt -> while ( expression ) statement
    def iteration_stmt(self):
        self.accept_val('while')
        self.accept_val('(')
        self.expression()
        self.accept_val(')')
        self.statement()

    # return-stmt -> return return-stmt' ;
    def return_stmt(self):
        self.accept_val('return')
        self.return_stmt_()
        self.accept_val(';')

    # return-stmt' -> expression | ϵ
    def return_stmt_(self):
        if self.next().val == '(' or self.next().type in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression()

    # expression -> ID expression' | ( expression ) term' additive-expression' simple-expression' | NUM term' additive-expression' simple-expression'
    def expression(self):
        if self.next().type == 'IDENTIFIER':
            self.accept_type('IDENTIFIER')
            self.expression_()
        elif self.next().val == '(':
            self.accept_val('(')
            self.expression()
            self.accept_val(')')
            self.term_()
            self.additive_expression_()
            self.simple_expression_()
        elif self.next().type in ['INTEGER', 'FLOAT']:
            self.number()
            self.term_()
            self.additive_expression_()
            self.simple_expression_()

    # expression' -> var' expression'' | ( args ) term' additive-expression' simple-expression'
    def expression_(self):
        if self.next().val == '(':
            self.accept_val('(')
            self.args()
            self.accept_val(')')
            self.additive_expression_()
            self.simple_expression_()
        else:
            self.var_()
            self.expression__()

    # expression'' -> = expression | term' additive-expression' simple-expression'
    def expression__(self):
        if self.next().val == '=':
            self.accept_val('=')
            self.expression()
        else:
            self.term_()
            self.additive_expression_()
            self.simple_expression_()

    # var -> ID var'
    def var(self):
        self.accept_type('IDENTIFIER')
        self.var_()

    # var' -> [ expression ] | ϵ
    def var_(self):
        if self.next().val == '[':
            self.accept_val('[')
            self.args()
            self.accept_val(']')

    # simple-expression' -> relop additive-expression | ϵ
    def simple_expression_(self):
        if self.next().type == 'RELOP':
            self.relop()
            self.additive_expression()

    # relop -> <= | < | > | >= | == | !=
    def relop(self):
        self.union(['<=', '<', '>', '>=', '==', '!='])

    # additive-expression -> term additive-expression'
    def additive_expression(self):
        self.term()
        self.additive_expression_()

    # additive-expression' -> addop term additive-expression' | ϵ
    def additive_expression_(self):
        if self.next().val in ['+', '-']:
            self.addop()
            self.term()
            self.additive_expression_()

    # addop -> + | -
    def addop(self):
        self.union(['+', '-'])

    # term -> factor term'
    def term(self):
        self.factor()
        self.term_()

    # term' -> mulop factor term' | ϵ
    def term_(self):
        if self.next().val in ['*', '/']:
            self.mulop()
            self.factor()
            self.term_()

    # mulop -> * | /
    def mulop(self):
        self.union(['*', '/'])

    # factor -> ( expression ) | ID factor' | NUM
    def factor(self):
        if self.next().val == '(':
            self.accept_val('(')
            self.expression()
            self.accept_val(')')
        elif self.next().type == 'IDENTIFIER':
            self.accept_type('IDENTIFIER')
            self.factor_()
        else:
            self.number()

    # factor' -> ( args ) | var'
    def factor_(self):
        if self.next().val == '(':
            self.accept_val('(')
            self.args()
            self.accept_val(')')
        else:
            self.var_()

    # call -> ID ( args )
    def call(self):
        self.accept_type('IDENTIFIER')
        self.accept_val('(')
        self.args()
        self.accept_val(')')

    # args -> arg-list | ϵ
    def args(self):
        if self.next().val == '(' or self.next().type in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.arg_list()

    # arg-list -> expression arg-list'
    def arg_list(self):
        self.expression()
        self.arg_list_()

    # arg-list' -> , expression arg-list' | ϵ
    def arg_list_(self):
        if self.next().val == ',':
            self.accept_val(',')
            self.expression()
            self.arg_list_()
