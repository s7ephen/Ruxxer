#!/usr/bin/env python
"""
    Ruxxer Grammar
    --------------
        This file contains all code related to the definition
    of the Ruxxer "grammar". It is important to note that the word
    "grammar" as we use it here refers to code responsible for 
    both the lexing AND the parsing. 
        None of the underlying Ruxxer types are defined within this
    file, all that stuff lives in rux_types.py and is imported here
    where it gets used when defining Ruxxer types and reserved
    words.
   
        The RuxxerParser class is a bit of a misnomer it contains
    methods specifically for the lexing and parsing, and as a part
    of its constructor builds the lexxer before parsing.    

        

"""

import sys
import readline
import ply.lex as lex
import ply.yacc as yacc
import os
import rux_types

global ruxxerRWD #The RuXXer "Reserved Word Dictionary"
                 #a simpler way to access all the reserved
                 #words  in Ruxxer's Grammar.

ruxxerRWD = {
    # type declarations
    'int' : 'INT',
    'long' : 'LONG',
    'short' : 'SHORT'
}

def check_types_against_reservewords():
    """
    This reads through all the RuXXer Primitives
    and checks that the currnt ruxxerRWD
    doesnt have anything that we forgot about.

    """
    for attr in dir(rux_types):
        a = getattr(rux_types, attr)
        if hasattr(a, "__rux_name__"):
            #ruxxerRWD.__setitem__(a.__rux_name__, a.__rux_name__.upper())
            if a.__rux_name__ not in ruxxerRWD.keys():
                print "Class", attr, "not currently registered with the Ruxxer Reserved Word Dictionary!"

check_types_against_reservewords() #We want this check to actually execute at
                                    #importation to make sure there are
                                    #no primitives that havent been added to the 
                                    #reserved word dictionary. 

class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule
        self.lexer = None

    def build_lexer(self):
        """
            Build the lexer/parser.
        """
        self.lexer = lex.lex(module=self, debug=self.debug)

    def test_lexer(self):
        """
            Test out the lexer.
        """
        self.lexer.input(data)
        while 1:
            tok = lexer.token()
            if not tok: break
            print tok
   
    def build_parser(self):
        """
        """
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)
 
    def parse_and_execute(self, code):
        """
            Receive a string of code, then lexically analyze it.
        Then "run" it.
        """
        yacc.parse(code)
    
class RuxxerParser(Parser):
    # **********************  T O K E N S  ************************
    tokens = ("NAME", "NUMBER", "EQUALS")
    t_EQUALS = r'='
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*' 
    
    def t_COMMENT(self, t):
        r'\#.*'
        #no return value makes comment possible.
        pass

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print "Integer value too large", t.value
            t.value = 0
        #print "parsed number %s" % repr(t.value)
        return t

    t_ignore = " \t"

    #   *** RUXXER TYPE DECLARATIONS ***
    #       Ruxxer requires that all variables be declared
    #    with variable declarations. 

    def t_SHORT(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = ruxxerRWD.get(t.value, 'SHORT')

    def t_LONG(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = ruxxerRWD.get(t.value, 'LONG')
        
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
 
    # *************************************************************
    # **************** P A R S I N G   R U L E S ******************
    precedence = ()

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.names[p[1]] = p[3]

    def p_statement_expr(self, p):
        'statement : expression'
        print p[1]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            print "Undefined name '%s'" % p[1]
            p[0] = 0

    def p_error(self, p):
        print "Syntax error at '%s'" % p.value

# *************************************************************

if __name__ == '__main__':
    bl = RuxxerParser()

