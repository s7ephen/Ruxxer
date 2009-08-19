#!/usr/bin/env python
import ply.lex as lex
import ply.yacc as yacc

# List of token names.   This is always required

class Parser:
    """
        A base class to implement lexer/parser from.
    """
    
    tokens = (
       'NAME',
       'NUMBER',
       'EQUALS',
       'LPAREN',
       'RPAREN',
    )

    types = {
        'int': 'INT'
    }

    # Regular expression rules for simple tokens
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_EQUALS  = r'='
    t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # A dictionary to store user created variables indexed
    # by name.

    names = {}

    def t_COMMENT(self, t):
        r'\#.*'
        pass # No return value. Token discarded

    # A regular expression rule with some action code
    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)    
        except ValueError:
            print "Line %d: Number %s is too large!" % (t.lineno,t.value)
            t.value = 0
        return t

#    def t_(self, t):
#        r'[a-zA-Z_][a-zA-Z_0-9]*'
#        t.type = self.names.get(t.value, 'NAME') #check if the id is in type
#                                                #reserved word dictionary
#        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'
    # Error handling rule

    def t_error(self, t):
        print "Illegal character '%s encountered.'" % t.value[0]
        t.lexer.skip(1)

    #------------- PARSING RULES ----------------
    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.names[p[1]] = p[3]

    def p_statement_expr(self, p):
        'statement : expression'
        print p[1]
        
    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
            print "Variable '%s' found!" % p[1]
        except LookupError:
            print "Undefined variable '%s'" % p[1]
            p[0] = 0

    # Error rule for syntax errors
    def p_error(self, p):
        print "Syntax error in input! '%s'" % p.value

def test_lexer(gram_module):
    lex.lex(module=gram_module)
    # Test it out
    data = '''
    1 2 3
    (10)
    '''

    # Give the lexer some input
    lex.input(data)

    # Tokenize
    print "--------"
    print "The DATA to be processed is:\n<SNIP>",data,"\n</SNIP>"
    print "--------"
    while 1:
        tok = lex.token()
        if not tok: break      # No more input
        #print repr(tok)
        print repr(tok.type), repr(tok.value), repr(tok.lineno), repr(tok.lexpos)
        print type(tok.type), type(tok.value), type(tok.lineno), type(tok.lexpos)
        print "-----"
        #print(dir(tok))

def test_parser(gram_module):
    #Build the Parser
    lex.lex(module=gram_module) #must build the lexer before grammar rules can be
                               #built
    yacc.yacc(module=gram_module)
    while 1:
        try:
           s = raw_input('calc input > ')
        except EOFError:
           break
        if not s: continue
        result = yacc.parse(s)
        if result:
            print "Result of parse: ", result

def test():
    test_gram = Parser()
    q = raw_input('Test [l]exer or [p]arser? >')
    if q[0] in ('l', 'L'):
        test_lexer(test_gram)
    elif q[0] in ('p', 'P'):
        test_parser(test_gram)
    
if __name__ == "__main__":
#    test_lexer()
    test()
