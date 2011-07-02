import os.path
import ply.yacc
from jspy.lexer import Lexer
from jspy import ast


class Parser(object):
    #
    # Note
    # ----
    #
    # Rule [ECMA-262 12.4] handled by `p_expression_statement` def:
    #
    #     expression_statement : [lookahead not in {LBRACE, FUNCTION}] expression SEMICOLON
    #
    # is not possible to implement directly in LR(1) parser and disallowing this
    # construct in LR(1) grammar would require duplicating a huge part of the rules.
    #
    # I've decided to live with PLY heuristic for reduce/reduce conflict instead
    # (choosing the first rule in grammar), which happens to be correct:
    #
    # state 74
    #
    #   (5) block -> LBRACE RBRACE .
    #   (36) object_literal -> LBRACE RBRACE .
    #
    # ! reduce/reduce conflict for LBRACE resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for LPAREN resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for PLUSPLUS resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for MINUSMINUS resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for PLUS resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for MINUS resolved using rule 5 (block -> LBRACE RBRACE .)
    # ! reduce/reduce conflict for SEMICOLON resolved using rule 5 (block -> LBRACE RBRACE .)
    #
    def __init__(self, lexer=None, start='program',
                 tabmodule=None,
                 outputdir=None,
                 debug=False):
        if outputdir is None:
            outputdir = os.path.dirname(__file__)
        if tabmodule is None:
            tabmodule = 'jspy._parser_' + start
        if lexer is None:
            lexer = Lexer()
        self.tokens = lexer.tokens
        self.lexer = lexer
        self.parser = ply.yacc.yacc(module=self,
                                    start=start,
                                    tabmodule=tabmodule,
                                    outputdir=outputdir,
                                    debug=debug)

    def parse(self, text):
        return self.parser.parse(text, lexer=self.lexer)

    # Resolve "dangling else" shift/reduce conflict according to [ECMA-262 12.5]
    precedence = (('right', 'ELSE'),)

    #
    # [ECMA-262 14] Program
    #
    def p_program(self, p):
        """program : statement_list_opt"""
        p[0] = ast.Block(statements=p[1])
    
    def p_statement_list(self, p):
        """statement_list : statement
                          | statement_list statement"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement_list_opt(self, p):
        """statement_list_opt : statement_list"""
        p[0] = p[1]

    def p_statement_list_opt_empty(self, p):
        """statement_list_opt : empty"""
        p[0] = []

    #
    # [ECMA-262 13] Function Definition
    #
    # TODO: Other ways of defining/declaring functions
    def p_function_expression(self, p):
        """function_expression : FUNCTION LPAREN formal_parameter_list_opt RPAREN block"""
        p[0] = ast.FunctionDefinition(parameters=p[3], body=p[5])
    
    def p_formal_parameter_list(self, p):
        """formal_parameter_list : identifier
                                 | formal_parameter_list COMMA identifier"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_formal_parameter_list_opt(self, p):
        """formal_parameter_list_opt : formal_parameter_list
                                     | empty"""
        p[0] = p[1]
    
    #
    # [ECMA-262 12] Statements
    #
    def p_statement(self, p):
        """statement : block
                     | variable_statement
                     | empty_statement
                     | expression_statement
                     | if_statement
                     | iteration_statement
                     | continue_statement
                     | break_statement
                     | return_statement
                     | debugger_statement"""
        p[0] = p[1]

    #
    # [ECMA-262 12.1] Block
    #
    def p_block(self, p):
        """block : LBRACE statement_list_opt RBRACE"""
        p[0] = ast.Block(statements=p[2])
    
    #
    # [ECMA-262 12.2] Variable Statement
    #
    def p_variable_statement(self, p):
        """variable_statement : VAR variable_declaration_list SEMICOLON"""
        p[0] = ast.VariableDeclarationList(declarations=p[2])
    
    def p_variable_declaration_list(self, p):
        """variable_declaration_list : variable_declaration
                                     | variable_declaration_list COMMA variable_declaration"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_variable_declaration(self, p):
        """variable_declaration : identifier
                                | identifier EQUALS assignment_expression"""
        if len(p) == 2:
            p[0] = ast.VariableDeclaration(identifier=p[1], initialiser=None)
        else:
            p[0] = ast.VariableDeclaration(identifier=p[1], initialiser=p[3])

    #
    # [ECMA-262 12.3] Empty Statement
    #
    def p_empty_statement(self, p):
        """empty_statement : SEMICOLON"""
        p[0] = ast.EmptyStatement()

    #
    # [ECMA-262 12.4] Expression Statement
    #
    def p_expression_statement(self, p):
        """expression_statement : expression SEMICOLON"""
        p[0] = ast.ExpressionStatement(expression=p[1])

    #
    # [ECMA-262 12.5] if Statement
    #
    def p_if_statement(self, p):
        """if_statement : IF LPAREN expression RPAREN statement ELSE statement
                        | IF LPAREN expression RPAREN statement"""
        if len(p) == 8:
            p[0] = ast.IfStatement(condition=p[3],
                                   true_statement=p[5],
                                   false_statement=p[7])
        else:
            p[0] = ast.IfStatement(condition=p[3],
                                   true_statement=p[5],
                                   false_statement=ast.EmptyStatement())

    #
    # [ECMA-262 12.6] Iteration Statements
    #
    def p_iteration_statement(self, p):
        """iteration_statement : do_while_statement
                               | while_statement"""
        # TODO : for_statement, for_var_statement, for_in_statement, for_var_in_statement
        p[0] = p[1]

    def p_while_statement(self, p):
        """while_statement : WHILE LPAREN expression RPAREN statement"""
        p[0] = ast.WhileStatement(condition=p[3], statement=p[5])

    def p_do_while_statement(self, p):
        """do_while_statement : DO statement WHILE LPAREN expression RPAREN SEMICOLON"""
        p[0] = ast.DoWhileStatement(condition=p[5], statement=p[2])

    #
    # [ECMA-262 12.7] The continue Statement
    #
    def p_continue_statement(self, p):
        """continue_statement : CONTINUE"""
        p[0] = ast.ContinueStatement()

    #
    # [ECMA-262 12.8] The break Statement
    #
    def p_break_statement(self, p):
        """break_statement : BREAK"""
        p[0] = ast.BreakStatement()

    #
    # [ECMA-262 12.9] The return Statement
    #
    def p_return_statement(self, p):
        """return_statement : RETURN expression_opt SEMICOLON"""
        p[0] = ast.ReturnStatement(expression=p[2])

    #
    # [ECMA-262 12.15] The debugger statement
    #
    def p_debugger_statement(self, p):
        """debugger_statement : DEBUGGER SEMICOLON"""
        p[0] = ast.DebuggerStatement()
    
    #
    # [ECMA-262 11.1] Primary Expressions
    #
    def p_primary_expression(self, p):
        """primary_expression : THIS
                              | identifier
                              | literal
                              | array_literal
                              | object_literal
                              | LPAREN expression RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_identifier(self, p):
        """identifier : ID"""
        p[0] = ast.Identifier(name=p[1])

    def p_literal(self, p):
        """literal : NUMBER
                   | STRING
                   | REGEXP
                   | TRUE
                   | FALSE
                   | NULL"""
        p[0] = ast.Literal(value=p[1])

    def p_array_literal(self, p):
        """array_literal : LBRACKET element_list_opt RBRACKET"""
        p[0] = ast.ArrayLiteral(items=p[2])

    def p_element_list(self, p):
        """element_list : element_list COMMA assignment_expression
                        | assignment_expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_element_list_opt(self, p):
        """element_list_opt : element_list"""
        p[0] = p[1]

    def p_element_list_opt_empty(self, p):
        """element_list_opt : empty"""
        p[0] = []
    
    def p_object_literal(self, p):
        """object_literal : LBRACE RBRACE
                          | LBRACE property_name_and_value_list RBRACE"""
        if len(p) == 3:
            p[0] = ast.ObjectLiteral(items=[])
        else:
            p[0] = ast.ObjectLiteral(items=p[2])

    def p_property_name_and_value_list(self, p):
        """property_name_and_value_list : property_assignment
                                        | property_name_and_value_list COMMA property_assignment"""
        if len(p) == 2:
            p[0] = dict([p[1]])
        else:
            import copy
            d = copy.deepcopy(p[1])
            d[p[3][0]] = p[3][1]
            p[0] = d

    def p_property_assignment(self, p):
        """property_assignment : property_name COLON assignment_expression"""
        p[0] = (p[1], p[3])

    def p_property_name(self, p):
        """property_name : ID
                         | STRING
                         | NUMBER"""
        p[0] = p[1]
    
    #
    # [ECMA-262 11.2] Left-Hand-Side Expressions
    #
    def p_member_expression(self, p):
        """member_expression : primary_expression
                             | function_expression
                             | property_access_expression
                             | constructor_expression"""
        p[0] = p[1]
        
    def p_property_access_expression(self, p):
        """property_access_expression : member_expression LBRACKET expression RBRACKET
                                      | member_expression PERIOD ID"""
        if len(p) == 5:
            p[0] = ast.PropertyAccess(obj=p[1], key=p[3])
        else:
            p[0] = ast.PropertyAccess(obj=p[1], key=ast.Literal(value=p[3]))
    
    def p_constructor_expression(self, p):
        """constructor_expression : NEW member_expression arguments"""
        p[0] = ast.Constructor(obj=p[2], arguments=p[3])
    
    def p_new_expression(self, p):
        """new_expression : member_expression
                          | NEW member_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Constructor(obj=p[2], arguments=[])
    
    def p_call_expression(self, p):
        """call_expression : member_expression arguments
                           | call_expression arguments"""
        p[0] = ast.FunctionCall(obj=p[1], arguments=p[2])

    def p_property_access_call_expression(self, p):
        """call_expression : call_expression LBRACE expression RBRACE
                           | call_expression PERIOD ID"""
        if len(p) == 5:
            p[0] = ast.PropertyAccesor(obj=p[1], key=p[3])
        else:
            p[0] = ast.PropertyAccesor(obj=p[1], key=ast.Literal(value=p[3]))

    def p_arguments(self, p):
        """arguments : LPAREN RPAREN
                     | LPAREN argument_list RPAREN"""
        if len(p) == 3:
            p[0] = []
        else:
            p[0] = p[2]
        
    def p_argument_list(self, p):
        """argument_list : assignment_expression
                         | argument_list COMMA assignment_expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_left_hand_side_expression(self, p):
        """left_hand_side_expression : new_expression
                                     | call_expression"""
        p[0] = p[1]
    
    #
    # [ECMA-262 11.3] Postfix Expressions
    #
    def p_postfix_expression(self, p):
        """postfix_expression : left_hand_side_expression
                              | left_hand_side_expression PLUSPLUS
                              | left_hand_side_expression MINUSMINUS"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(op='postfix' + p[2], expression=p[1])
        
    #
    # [ECMA-262 11.4] Unary Operators
    #
    def p_unary_expression(self, p):
        """unary_expression : postfix_expression
                            | DELETE unary_expression
                            | VOID unary_expression
                            | TYPEOF unary_expression
                            | PLUSPLUS unary_expression
                            | MINUSMINUS unary_expression
                            | PLUS unary_expression
                            | MINUS unary_expression
                            | NOT unary_expression
                            | LNOT unary_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(op=p[1], expression=p[2])
    
    #
    # [ECMA-262 11.5] Multiplicative Operators
    #
    def p_multiplicative_expression(self, p):
        """multiplicative_expression : unary_expression
                                     | multiplicative_expression TIMES unary_expression
                                     | multiplicative_expression DIVIDE unary_expression
                                     | multiplicative_expression MOD unary_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])
    
    #
    # [ECMA-262 11.6] Additive Operators
    #
    def p_additive_expression(self, p):
        """additive_expression : multiplicative_expression
                               | additive_expression PLUS multiplicative_expression
                               | additive_expression MINUS multiplicative_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    #
    # [ECMA-262 11.7] Bitwise Shift Operators
    #
    def p_shift_expression(self, p):
        """shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])


    #
    # [ECMA-262 11.8] Relational Operators
    #
    def p_relational_expression(self, p):
        """relational_expression : shift_expression
                                 | relational_expression LT shift_expression
                                 | relational_expression LE shift_expression
                                 | relational_expression GT shift_expression
                                 | relational_expression GE shift_expression
                                 | relational_expression INSTANCEOF shift_expression
                                 | relational_expression IN shift_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    #
    # [ECMA-262 11.9] Equality Operators
    #
    def p_equality_expression(self, p):
        """equality_expression : relational_expression
                               | equality_expression EQ relational_expression
                               | equality_expression NEQ relational_expression
                               | equality_expression STRICTEQ relational_expression
                               | equality_expression STRICTNEQ relational_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    #
    # [ECMA-262 11.10] Binary Bitwise Operators
    #
    def p_bitwise_and_expression(self, p):
        """bitwise_and_expression : equality_expression
                                  | bitwise_and_expression AND equality_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    def p_bitwise_xor_expression(self, p):
        """bitwise_xor_expression : bitwise_and_expression
                                  | bitwise_xor_expression XOR bitwise_and_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    def p_bitwise_or_expression(self, p):
        """bitwise_or_expression : bitwise_xor_expression
                                 | bitwise_or_expression OR bitwise_xor_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    #
    # [ECMA-262 11.11] Binary Logical Operators
    #
    def p_logical_and_expression(self, p):
        """logical_and_expression : bitwise_or_expression
                                  | logical_and_expression LAND bitwise_or_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    def p_logical_or_expression(self, p):
        """logical_or_expression : logical_and_expression
                                 | logical_or_expression LOR logical_and_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(op=p[2], left_expression=p[1], right_expression=p[3])

    #
    # [ECMA-262 11.12] Conditional Operator (? :)
    #
    def p_conditional_expression(self, p):
        """conditional_expression : logical_or_expression
                                  | logical_or_expression CONDOP assignment_expression COLON assignment_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.ConditionalOp(condition=p[1], true_expression=p[3], false_expression=p[5])
        
    #
    # [ECMA-262 11.13] Assignment Operators
    #
    def p_assignment_expression(self, p):
        """assignment_expression : conditional_expression
                                 | left_hand_side_expression assignment_operator assignment_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assignment(op=p[2], reference=p[1], expression=p[3])
    
    def p_assignment_operator(self, p):
        """assignment_operator : EQUALS
                               | TIMESEQUAL
                               | DIVEQUAL
                               | MODEQUAL
                               | PLUSEQUAL
                               | MINUSEQUAL
                               | LSHIFTEQUAL
                               | RSHIFTEQUAL
                               | ANDEQUAL
                               | XOREQUAL
                               | OREQUAL"""
        p[0] = p[1]
    
    #
    # [ECMA-262 11.14] Comma Operator (,)
    #
    def p_expression(self, p):
        """expression : assignment_expression
                      | expression COMMA assignment_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.MultiExpression(left_expression=p[1], right_expression=p[3])

    def p_expression_opt(self, p):
        """expression_opt : expression
                          | empty"""
        p[0] = p[1]

    #
    # Empty grammar rule (used in optional rules)
    #
    def p_empty(self, p):
        """empty :  """
        p[0] = None

    # Error handling
    def p_error(self, p):
        raise TypeError('Parse error before: %r!' % p)

