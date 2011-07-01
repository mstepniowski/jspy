import ply.yacc
from jspy.lexer import Lexer
from jspy import ast


class Parser(object):
    def __init__(self, lexer=None, start='expression', debug=False):
        if lexer is None:
            lexer = Lexer()
        self.tokens = lexer.tokens
        self.lexer = lexer
        self.parser = ply.yacc.yacc(module=self, 
                                    start=start,
                                    debug=debug)

    def parse(self, text):
        return self.parser.parse(text, lexer=self.lexer)

    #
    # [ECMA-262 11.1] Primary Expressions
    #
    def p_primary_expression(self, p):
        """primary_expression : THIS
                              | literal
                              | array_literal
                              | object_literal
                              | LPAREN expression RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_primary_expression_id(self, p):
        """primary_expression : ID"""
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
        """array_literal : LBRACKET element_list RBRACKET"""
        p[0] = ast.ArrayLiteral(items=p[2])

    def p_element_list(self, p):
        """element_list : element_list COMMA assignment_expression
                        | assignment_expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_object_literal(self, p):
        """object_literal : LBRACE RBRACE
                          | LBRACE property_name_and_value_list RBRACE"""
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
                             | property_access_expression
                             | constructor_expression"""
        # TODO: function_expression
        p[0] = p[1]
        
    def p_property_access_expression(self, p):
        """property_access_expression : member_expression LBRACE expression RBRACE
                                      | member_expression PERIOD ID"""
        if len(p) == 5:
            p[0] = ast.PropertyAccesor(obj=p[1], key=p[3])
        else:
            p[0] = ast.PropertyAccesor(obj=p[1], key=ast.Literal(value=p[3]))
    
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
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + p[3]
    
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


    # Needed to avoid confusing the `in` operator within relational
    # expression with the `in` operator in a `for` statement
    def p_relational_expression_no_in(self, p):
        """relational_expression_no_in : shift_expression
                                       | relational_expression_no_in LT shift_expression
                                       | relational_expression_no_in LE shift_expression
                                       | relational_expression_no_in GT shift_expression
                                       | relational_expression_no_in GE shift_expression
                                       | relational_expression_no_in INSTANCEOF shift_expression"""
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

    def p_equality_expression_no_in(self, p):
        """equality_expression_no_in : relational_expression_no_in
                               | equality_expression_no_in EQ relational_expression_no_in
                               | equality_expression_no_in NEQ relational_expression_no_in
                               | equality_expression_no_in STRICTEQ relational_expression_no_in
                               | equality_expression_no_in STRICTNEQ relational_expression_no_in"""
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

    def p_bitwise_and_expression_no_in(self, p):
        """bitwise_and_expression_no_in : equality_expression_no_in
                                        | bitwise_and_expression_no_in AND equality_expression_no_in"""
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

    def p_bitwise_xor_expression_no_in(self, p):
        """bitwise_xor_expression_no_in : bitwise_and_expression_no_in
                                        | bitwise_xor_expression_no_in XOR bitwise_and_expression_no_in"""
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

    def p_bitwise_or_expression_no_in(self, p):
        """bitwise_or_expression_no_in : bitwise_xor_expression_no_in
                                       | bitwise_or_expression_no_in OR bitwise_xor_expression_no_in"""
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

    def p_logical_and_expression_no_in(self, p):
        """logical_and_expression_no_in : bitwise_or_expression_no_in
                                        | logical_and_expression_no_in LAND bitwise_or_expression_no_in"""
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

    def p_logical_or_expression_no_in(self, p):
        """logical_or_expression_no_in : logical_and_expression_no_in
                                       | logical_or_expression_no_in LOR logical_and_expression_no_in"""
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
        
    def p_conditional_expression_no_in(self, p):
        """conditional_expression_no_in : logical_or_expression_no_in
                                        | logical_or_expression_no_in CONDOP assignment_expression_no_in COLON assignment_expression_no_in"""
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
    
    def p_assignment_expression_no_in(self, p):
        """assignment_expression_no_in : conditional_expression_no_in
                                       | left_hand_side_expression assignment_operator assignment_expression_no_in"""
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
    
    def p_expression_no_in(self, p):
        """expression_no_in : assignment_expression_no_in
                            | expression_no_in COMMA assignment_expression_no_in"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.MultiExpression(left_expression=p[1], right_expression=p[3])
    
    # Error handling
    def p_error(self, p):
        raise TypeError('Parse error before: %r!' % p)

