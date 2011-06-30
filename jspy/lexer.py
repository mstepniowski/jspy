import ply.lex as lex


class Lexer(object):
    def __init__(self):
        self.lexer = lex.lex(module=self)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()
    
    # Reserved keywords
    keywords = (
        'BREAK', 'DO', 'INSTANCEOF', 'TYPEOF',
        'CASE', 'ELSE', 'NEW', 'VAR', 'CATCH', 'FINALLY', 'RETURN', 'VOID',
        'CONTINUE', 'FOR', 'SWITCH', 'WHILE', 'DEBUGGER', 'FUNCTION', 'THIS',
        'WITH', 'DEFAULT', 'IF', 'THROW', 'DELETE', 'IN', 'TRY')

    keyword_map = {}
    for r in keywords:
        keyword_map[r.lower()] = r
    
    tokens = keywords + (
        # Comments
        'COMMENT', 'CPPCOMMENT',
        
        # Literals
        'ID', 'NUMBER', 'STRING', 'REGEXP', 'TRUE', 'FALSE', 'NULL',
        
        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', # + - * / %
        'OR', 'AND', 'NOT', 'XOR',                 # | & ~ ^
        'LOR', 'LAND', 'LNOT',                     # || && !
        'STRICTEQ', 'STRICTNEQ',                   # ===, !==
        'LSHIFT', 'RSHIFT',                        # <<, >>
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ',       # < <= > >= == !=

        # Assignment operators
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 
        'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 
        'OREQUAL',
        
        # Increment/decrement 
        'PLUSPLUS', 'MINUSMINUS',

        # Conditional operator (?)
        'CONDOP',

        # Delimiters
        'LPAREN', 'RPAREN',     # ( )
        'LBRACKET', 'RBRACKET', # [ ]
        'LBRACE', 'RBRACE',     # { }
        'COMMA', 'PERIOD',      # , .
        'SEMICOLON', 'COLON'    # ; :
    )

    # Literals
    t_TRUE    = r'true'
    t_FALSE   = r'false'
    t_NULL    = r'null'
    
    # Operators
    t_PLUS              = r'\+'
    t_MINUS             = r'-'
    t_TIMES             = r'\*'
    t_DIVIDE            = r'/'
    t_MOD               = r'%'
    t_OR                = r'\|'
    t_AND               = r'&'
    t_NOT               = r'~'
    t_XOR               = r'\^'
    t_LOR               = r'\|\|'
    t_LAND              = r'&&'
    t_LNOT              = r'!'
    t_STRICTEQ          = r'==='
    t_STRICTNEQ         = r'!=='
    t_LSHIFT            = r'<<'
    t_RSHIFT            = r'>>'
    t_LT                = r'<'
    t_GT                = r'>'
    t_LE                = r'<='
    t_GE                = r'>='
    t_EQ                = r'=='
    t_NEQ               = r'!='

    # Assignment operators
    t_EQUALS            = r'='
    t_TIMESEQUAL        = r'\*='
    t_DIVEQUAL          = r'/='
    t_MODEQUAL          = r'%='
    t_PLUSEQUAL         = r'\+='
    t_MINUSEQUAL        = r'-='
    t_LSHIFTEQUAL       = r'<<='
    t_RSHIFTEQUAL       = r'>>='
    t_ANDEQUAL          = r'&='
    t_OREQUAL           = r'\|='
    t_XOREQUAL          = r'\^='

    # Conditional operator
    t_CONDOP            = r'\?'

    # Delimiters
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_LBRACE    = r'\{'
    t_RBRACE    = r'\}'
    t_COMMA     = r','
    t_PERIOD    = r'\.'
    t_SEMICOLON = r';'
    t_COLON     = r':'
    
    # Comment (C-Style)
    def t_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        return t

    # Comment (C++-Style)
    def t_CPPCOMMENT(self, t):
        r'//.*\n'
        t.lexer.lineno += 1
        return t

    # Identifiers and keywords
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.keyword_map.get(t.value, 'ID')
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = float(t.value)
        return t

    def t_STRING(self, t):
        r""""([^\\\n]|(\\.))*?"|'([^\\\n]|(\\.))*?'"""
        t.value = t.value[1:-1]
        return t

    def t_REGEXP(self, t):
        r"""/([^\\\n]|(\\.))*?/[a-zA-Z]*"""
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self, t):
        print "Illegal character '%s' at line %d" % (t.value[0], t.lexer.lineno)
        t.lexer.skip(1)

