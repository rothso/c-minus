from typing import List, Tuple, Union


def parse(tokens: List[Tuple[str, str]]) -> bool:
    parser = CMinusParser(tokens)
    try:
        parser.parse()
        return True
    except:
        return False


class CMinusParser:

    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens

    def accept(self, token: Union[str, Tuple[str, str]]):
        head = self.tokens.pop(0)
        if (isinstance(token, tuple) and head != token) or (
                isinstance(token, str) and head[0] != token):
            raise Exception('unexpected token', head)

    def next(self) -> Tuple[str, str]:
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
            if self.next()[1] in ['int', 'float', 'void']:
                self.declaration()
                self.declaration_list_()
        except IndexError:
            return  # end of program

    # declaration -> type-specifier ID declaration'
    def declaration(self):
        self.type_specifier()
        self.accept('IDENTIFIER')
        self.declaration_()

    # declaration' -> var-declaration' ; | ( params ) compound-stmt
    def declaration_(self):
        if self.next()[1] in ['[', ';']:
            self.var_declaration_()
            self.accept(('PUNCTUATION', ';'))
        elif self.next()[1] == '(':
            self.accept(('PUNCTUATION', '('))
            self.params()
            self.accept(('PUNCTUATION', ')'))
            self.compound_stmt()
        else:
            raise Exception("Parse error")

    # var-declaration' -> [ NUM ] | ϵ
    def var_declaration_(self):
        if self.next()[1] == '[':
            self.accept(('PUNCTUATION', '['))
            self.number()
            self.accept(('PUNCTUATION', ']'))

    # number -> INTEGER | FLOAT
    def number(self):
        if self.next()[0] == 'INTEGER':
            self.accept('INTEGER')
        else:
            self.accept('FLOAT')

    # type-specifier -> int | float | void
    def type_specifier(self):
        for t in ['int', 'float', 'void']:
            if self.next()[1] == t:
                self.accept(('KEYWORD', t))
                return
        raise Exception("Parse error")

    # params -> int ID param' param-list' | float ID param' param-list' | void params'
    def params(self):
        if self.next()[1] in ['int', 'float']:
            self.accept(('KEYWORD', self.next()[1]))
            self.accept('IDENTIFIER')
            self.param_()
            self.param_list_()
        elif self.next()[1] == 'void':
            self.accept(('KEYWORD', 'void'))
            self.params_()

    # params' -> ID param' param-list' | ϵ
    def params_(self):
        if self.next()[0] == 'IDENTIFIER':
            self.accept('IDENTIFIER')
            self.param_()
            self.param_list_()

    # param-list' -> , param param-list' | ϵ
    def param_list_(self):
        if self.next()[1] == ',':
            self.accept(('PUNCTUATION', ','))
            self.param()
            self.param_list_()

    # param -> type-specifier ID param'
    def param(self):
        self.type_specifier()
        self.accept('IDENTIFIER')
        self.param_()

    # param' -> [] | ϵ
    def param_(self):
        if self.next()[1] == '[':
            self.accept(('PUNCTUATION', '['))
            self.accept(('PUNCTUATION', ']'))

    # compound-stmt -> { local-declarations statement-list }
    def compound_stmt(self):
        self.accept(('PUNCTUATION', '{'))
        self.local_declarations()
        self.statement_list()
        self.accept(('PUNCTUATION', '}'))

    # local-declarations -> local-declarations'
    def local_declarations(self):
        self.local_declarations_()

    # local-declarations' -> type-specifier ID var-declaration' ; local-declarations' | ϵ
    def local_declarations_(self):
        if self.next()[1] in ['int', 'float', 'void']:
            self.type_specifier()
            self.accept('IDENTIFIER')
            self.var_declaration_()
            self.accept(('PUNCTUATION', ';'))
            self.local_declarations_()

    # statement-list -> statement-list'
    def statement_list(self):
        self.statement_list_()

    # statement-list' -> statement statement-list' | ϵ
    def statement_list_(self):
        if self.next()[1] in ['(', ';', 'if', 'return', 'while', '{'] or (
                self.next()[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']):
            self.statement()
            self.statement_list_()

    # statement -> expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
    def statement(self):
        if self.next()[1] in ['(', ';'] or self.next()[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression_stmt()
        elif self.next()[1] == '{':
            self.compound_stmt()
        elif self.next()[1] == 'if':
            self.selection_stmt()
        elif self.next()[1] == 'while':
            self.iteration_stmt()
        elif self.next()[1] == 'return':
            self.return_stmt()

    # expression-stmt -> expression ; | ;
    def expression_stmt(self):
        if self.next()[1] == '(' or self.next()[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression()
        self.accept(('PUNCTUATION', ';'))

    # selection-stmt -> if ( expression ) statement selection-stmt'
    def selection_stmt(self):
        self.accept(('KEYWORD', 'if'))
        self.accept(('PUNCTUATION', '('))
        self.expression()
        self.accept(('PUNCTUATION', ')'))
        self.statement()
        self.selection_stmt_()

    # selection-stmt' -> else statement | ϵ
    def selection_stmt_(self):
        if self.next()[1] == 'else':
            self.accept(('KEYWORD', 'else'))
            self.statement()

    # iteration-stmt -> while ( expression ) statement
    def iteration_stmt(self):
        self.accept(('KEYWORD', 'while'))
        self.accept(('PUNCTUATION', '('))
        self.expression()
        self.accept(('PUNCTUATION', ')'))
        self.statement()

    # return-stmt -> return return-stmt' ;
    def return_stmt(self):
        self.accept(('KEYWORD', 'return'))
        self.return_stmt_()
        self.accept(('PUNCTUATION', ';'))

    # return-stmt' -> expression | ϵ
    def return_stmt_(self):
        if self.next()[1] == '(' or self.next()[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.expression()

    # expression -> ID expression' | ( expression ) term' additive-expression' simple-expression' | NUM term' additive-expression' simple-expression'
    def expression(self):
        if self.next()[0] == 'IDENTIFIER':
            self.accept('IDENTIFIER')
            self.expression_()
        elif self.next()[1] == '(':
            self.accept(('PUNCTUATION', '('))
            self.expression()
            self.accept(('PUNCTUATION', ')'))
            self.term_()
            self.additive_expression_()
            self.simple_expression_()
        elif self.next()[0] in ['INTEGER', 'FLOAT']:
            self.number()
            self.term_()
            self.additive_expression_()
            self.simple_expression_()

    # expression' -> var' expression'' | ( args ) term' additive-expression' simple-expression'
    def expression_(self):
        if self.next()[1] == '(':
            self.accept(('PUNCTUATION', '('))
            self.args()
            self.accept(('PUNCTUATION', ')'))
            self.additive_expression_()
            self.simple_expression_()
        else:
            self.var_()
            self.expression__()

    # expression'' -> = expression | term' additive-expression' simple-expression'
    def expression__(self):
        if self.next()[1] == '=':
            self.accept(('PUNCTUATION', '='))
            self.expression()
        else:
            self.term_()
            self.additive_expression_()
            self.simple_expression_()

    # var -> ID var'
    def var(self):
        self.accept('IDENTIFIER')
        self.var_()

    # var' -> [ expression ] | ϵ
    def var_(self):
        if self.next()[1] == '[':
            self.accept(('PUNCTUATION', '['))
            self.args()
            self.accept(('PUNCTUATION', ']'))

    # simple-expression' -> relop additive-expression | ϵ
    def simple_expression_(self):
        if self.next()[0] == 'EQUALITYOP':
            self.relop()
            self.additive_expression()

    # relop -> <= | < | > | >= | == | !=
    def relop(self):
        for t in ['<=', '<', '>', '>=', '==', '!=']:
            if self.next()[1] == t:
                self.accept(('EQUALITYOP', t))
                return
        raise Exception("Parse error")

    # additive-expression -> term additive-expression'
    def additive_expression(self):
        self.term()
        self.additive_expression_()

    # additive-expression' -> addop term additive-expression' | ϵ
    def additive_expression_(self):
        if self.next()[1] in ['+', '-']:
            self.addop()
            self.term()
            self.additive_expression_()

    # addop -> + | -
    def addop(self):
        for t in ['+', '-']:
            if self.next()[1] == t:
                self.accept(('MATHOP', t))
                return
        raise Exception("Parse error")

    # term -> factor term'
    def term(self):
        self.factor()
        self.term_()

    # term' -> mulop factor term' | ϵ
    def term_(self):
        if self.next()[1] in ['*', '/']:
            self.mulop()
            self.factor()
            self.term_()

    # mulop -> * | /
    def mulop(self):
        for t in ['*', '/']:
            if self.next()[1] == t:
                self.accept(('MATHOP', t))
                return
        raise Exception("Parse error")

    # factor -> ( expression ) | ID factor' | NUM
    def factor(self):
        if self.next()[1] == '(':
            self.accept(('PUNCTUATION', '('))
            self.expression()
            self.accept(('PUNCTUATION', ')'))
        elif self.next()[0] == 'IDENTIFIER':
            self.accept('IDENTIFIER')
            self.factor_()
        else:
            self.number()

    # factor' -> ( args ) | var'
    def factor_(self):
        if self.next()[1] == '(':
            self.accept(('PUNCTUATION', '('))
            self.args()
            self.accept(('PUNCTUATION', ')'))
        else:
            self.var_()

    # call -> ID ( args )
    def call(self):
        self.accept('IDENTIFIER')
        self.accept(('PUNCTUATION', '('))
        self.args()
        self.accept(('PUNCTUATION', ')'))

    # args -> arg-list | ϵ
    def args(self):
        if self.next()[1] == '(' or self.next()[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            self.arg_list()

    # arg-list -> expression arg-list'
    def arg_list(self):
        self.expression()
        self.arg_list_()

    # arg-list' -> , expression arg-list' | ϵ
    def arg_list_(self):
        if self.next()[1] == ',':
            self.accept(('PUNCTUATION', ','))
            self.expression()
            self.arg_list_()
