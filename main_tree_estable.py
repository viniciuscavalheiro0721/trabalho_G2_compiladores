from yaml import dump

from ply import lex
from ply.yacc import yacc
from tree import append_node, new_leaf, new_node

tokens = (
    'TO',
    'ID',
    'NUMBER',
    'END',
    'COLON',
    'IF',
    'THEN',
    'ELSE',
    'WHILE',
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN"
)

reserveds = {
   'IF': 'IF',
   'THEN': 'THEN',
   'ELSE': 'ELSE',
   'END': 'END',
   'WHILE': 'WHILE',
   'NOT': 'NOT',
   'TO': 'TO',
   'AND': 'AND',
   'OR': 'OR',
   'SET': 'SET',
}


t_ignore = ' \t'

t_COLON = r':'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'


@lex.TOKEN(r"[+-]?\d+([.]\d*)?")
def t_NUMBER(token):  # pylint: disable=invalid-name
    """Extract a number."""
    if "." in token.value:
        token.value = float(token.value)
    else:
        token.value = int(token.value)
    return token


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserveds.get(t.value.upper(), 'ID')
    return t


def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)


def lexer_():
    """Create a new lexer object."""
    return lex.lex()


lexer = lexer_()

# final lexer


def p_program(p):
    """program : statement_or_decl"""
    node = new_node("Program")
    append_node(node, p[1])
    p[0] = node


def p_statement_or_decl(p):
    """statement_or_decl : statement statement_or_decl   
                        |
    """
    if len(p) > 2:
        if p[2] is None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]
            p[0].extend(p[2])
    

def p_decl_fn(p):
    'decl_fn : TO ID args_list statement_or_decl END'
   
    node = new_node("Declare function")
    append_node(node, new_leaf("TO"))
    append_node(node, new_leaf("ID", value=p[2]))
    append_node(node, p[3])
    append_node(node, p[4])
    append_node(node, new_leaf(p.slice[4].type, value=p[5]))
    p[0] = node


def p_args_list(p):
    """args_list :
                    | args args_list
    """
    if len(p) > 2:
        if p[2] is None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]
            p[0].extend(p[2])


def p_args(p):
    """args : COLON id
                  | number
    """
    if len(p) > 2:
        p[0] = ('args', p[2])
    else:
        p[0] = ('args', p[1])


def p_statement(p):
    """statement : decl_fn 
                 | call_function
                 | if
                 | if_else
                 | while
                 | expression
    """

    node = new_node("statement")
    append_node(node, p[1])
    p[0] = node
  

def p_call_function(p):
    """call_function : ID args_list"""
    node = new_node("Call function")
    append_node(node, new_leaf("ID", value=p[1]))
    append_node(node, p[2])
    p[0] = node
    


def p_number(p):
    'number : NUMBER'
    p[0] = ('number', p[1])


def p_id(p):
    'id : ID'
    p[0] = ('Identifier', p[1])


def p_error(p):
    print(f'Syntax error at {p.value!r}')


def p_if(p):
    """if : IF ID THEN statement_or_decl END"""
    node = new_node("If Then")
    append_node(node, new_leaf("IF", value=p[1]))
    append_node(node, new_leaf("ID", value=p[2]))
    append_node(node, new_leaf("THEN", value=p[3]))
    append_node(node, p[4])
    append_node(node, new_leaf("END", value=p[5]))
    p[0] = node



def p_if_else(p):
    """if_else : IF ID THEN statement_or_decl ELSE statement_or_decl END"""
    node = new_node("If Then Else")
    append_node(node, new_leaf("IF", value=p[1]))
    append_node(node, new_leaf("ID", value=p[2]))
    append_node(node, new_leaf("THEN", value=p[3]))
    append_node(node, p[4])
    append_node(node, new_leaf("ELSE", value=p[5]))
    append_node(node, p[6])
    p[0] = node
    


def p_while(p):
    """while : WHILE ID statement_or_decl END"""
    node = new_node("while")
    append_node(node, new_leaf("WHILE", value=p[1]))
    append_node(node, new_leaf("ID", value=p[2]))
    append_node(node, p[3])
    append_node(node, new_leaf("END", value=p[4]))
    p[0] = node
    


def p_factor_unary(p):
    '''
    factor : PLUS factor
           | MINUS factor
    '''
    node = new_node("MATH EXPRESSION")
    append_node(node, new_leaf(p.slice[1].type, value=p[1]))
    append_node(node, p[2])
    p[0] = node
 


def p_factor_grouped(p):
    '''
    factor : LPAREN expression RPAREN
    '''

    node = new_node("MATH EXPRESSION")
    append_node(node, "LPAREN", value=p[1])
    append_node(node, p[2])
    append_node(node, "RPAREN", value=p[1])
    p[0] = node



def p_expression(p):
    '''
    expression : term PLUS term
               | term MINUS term
    '''

    node = new_node("EXPRESSION")
    append_node(node, p[1])
    append_node(node, new_leaf(p.slice[2].type, value=p[2]))
    append_node(node, p[3])
    p[0] = node
    


def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]


def p_term(p):
    '''
    term : factor TIMES factor
         | factor DIVIDE factor
    '''
    node = new_node("EXPRESSION")
    append_node(node, p[1])
    append_node(node, new_leaf(p.slice[2].type, value=p[2]))
    append_node(node, p[3])
    p[0] = node
  


def p_term_factor(p):
    '''
    term : factor
    '''
    p[0] = p[1]


def p_factor_number(p):
    '''
    factor : NUMBER
    '''

    node = new_node("factor number")
    append_node(node, new_leaf("NUMBER", value=p[1]))
    p[0] = node
  


parser = yacc()

expression = """
TO SQUARE :length
    FORWARD :length
    RIGHT 10
    FORWARD :length
    RIGHT 20
    FORWARD :length
    RIGHT 30
    FORWARD :length
    RIGHT 40
END

SETXY 50
SQUARE 60


"""
expression_result = parser.parse(expression)
print(dump(expression_result, sort_keys=False, indent=2))