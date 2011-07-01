import unittest2
from jspy.parser import Parser
from jspy import ast, js


class TestParseExpression(unittest2.TestCase):
    def test_primary(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('{7: [9, 10, "ala ma kota"], "ala ma kota": {3: 4}}'),
                         ast.ObjectLiteral(
                items={7: ast.ArrayLiteral(items=[ast.Literal(value=9),
                                                  ast.Literal(value=10),
                                                  ast.Literal(value='ala ma kota')]),
                       'ala ma kota': ast.ObjectLiteral(items={3: ast.Literal(value=4)})}))

    def test_binary_op(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('1 + 2 * 7'),
                         ast.BinaryOp(op='+',
                                      left_expression=ast.Literal(value=1),
                                      right_expression=ast.BinaryOp(op='*',
                                                                    left_expression=ast.Literal(value=2),
                                                                    right_expression=ast.Literal(value=7))))
    def test_unary_op(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('+-1'),
                         ast.UnaryOp(op='+',
                                     expression=ast.UnaryOp(op='-',
                                                            expression=ast.Literal(value=1))))

    def test_prefix_op(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('++x'),
                         ast.UnaryOp(op='++',
                                     expression=ast.Identifier(name='x')))

    def test_compound_assignment(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('x /= 5 - 2'),
                         ast.Assignment(op='/=',
                                        reference=ast.Identifier(name='x'),
                                        expression=ast.BinaryOp(op='-',
                                                                left_expression=ast.Literal(value=5),
                                                                right_expression=ast.Literal(value=2))))


class TestEvalExpression(unittest2.TestCase):
    def eval_expression(self, expression, context=None):
        if context is None:
            context = js.ExecutionContext({})
        if not isinstance(context, js.ExecutionContext):
            context = js.ExecutionContext(context)
        expression_ast = Parser(start='expression').parse(expression)
        return js.get_value(expression_ast.eval(context))
    
    def test_binary_op(self):
        self.assertEqual(self.eval_expression('1 + 2 * 7'), 15)

    def test_binary_op_reference(self):
        self.assertEqual(self.eval_expression('x + y * 3', {'x': 3, 'y': 2}), 9)

    def test_unary_op(self):
        self.assertEqual(self.eval_expression('+-1'), -1)

    def test_parens(self):
        self.assertEqual(self.eval_expression('(1 + 2) * 7'), 21)

    def test_reference(self):
        self.assertEqual(self.eval_expression('x', {'x': 5}), 5)

    def test_condition_op(self):
        self.assertEqual(self.eval_expression('"ham" === "spam" ? "SPAMSPAMSPAM" : "no spam"'), 'no spam')

    def test_prefix_op(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval_expression('++x', context), 4)
        self.assertEqual(context['x'], 4)
        self.assertEqual(self.eval_expression('--x', context), 3)
        self.assertEqual(context['x'], 3)

    def test_postfix_op(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval_expression('x++', context), 3)
        self.assertEqual(context['x'], 4)
        self.assertEqual(self.eval_expression('x--', context), 4)
        self.assertEqual(context['x'], 3)
        
    def test_assignment(self):
        self.assertEqual(self.eval_expression('x = 7, x', {'x': 5}), 7)

    def test_compound_assignment(self):
        context = js.ExecutionContext({'x': 15})        
        self.assertEqual(self.eval_expression('x /= 5 - 2', context), 5)
        self.assertEqual(context['x'], 5)


class TestParseStatement(unittest2.TestCase):
    def test_block(self):
        parser = Parser(start='statement')
        self.assertEqual(parser.parse('{ 1; 3; }'),
                         ast.Block(statements=[ast.ExpressionStatement(expression=ast.Literal(value=1)),
                                               ast.ExpressionStatement(expression=ast.Literal(value=3))]))
    
    def test_variable_statement(self):
        parser = Parser(start='statement')
        self.assertEqual(parser.parse('var x = 7, y = 5;'),
                         ast.VariableDeclarationList(
                declarations=[ast.VariableDeclaration(identifier=ast.Identifier(name='x'),
                                                      initialiser=ast.Literal(value=7)),
                              ast.VariableDeclaration(identifier=ast.Identifier(name='y'),
                                                      initialiser=ast.Literal(value=5))]))

    def test_variable_statement_without_initialiser(self):
        parser = Parser(start='statement')
        self.assertEqual(parser.parse('var x, y = 5;'),
                         ast.VariableDeclarationList(
                declarations=[ast.VariableDeclaration(identifier=ast.Identifier(name='x'),
                                                      initialiser=None),
                              ast.VariableDeclaration(identifier=ast.Identifier(name='y'),
                                                      initialiser=ast.Literal(value=5))]))


class TestEvalStatement(unittest2.TestCase):
    def eval(self, stmt, context=None):
        if context is None:
            context = js.ExecutionContext({})
        if not isinstance(context, js.ExecutionContext):
            context = js.ExecutionContext(context)
        stmt_ast = Parser(start='statement', debug=True).parse(stmt)
        return js.get_value(stmt_ast.eval(context))

    def test_empty_statement(self):
        self.assertEqual(self.eval(';'), js.EMPTY_COMPLETION)

    def test_block(self):
        self.assertEqual(self.eval('{ 1; 3; }'), js.Completion(js.NORMAL, 3, js.EMPTY))
    
    def test_expression_statement(self):
        self.assertEqual(self.eval('1 + 2 * 7;'), js.Completion(js.NORMAL, 15, js.EMPTY))

    def test_nested_blocks(self):
        self.assertEqual(self.eval('{ 1; {3; 2;}}'), js.Completion(js.NORMAL, 2, js.EMPTY))

    def test_block_with_empty_statements(self):
        self.assertEqual(self.eval('{7;;}'), js.Completion(js.NORMAL, 7, js.EMPTY))

    def test_variable_declaration_list(self):
        context = js.ExecutionContext({})
        self.assertEqual(self.eval('var x = 7, y = 5;', context), js.EMPTY_COMPLETION)
        self.assertEqual(context['x'], 7)
        self.assertEqual(context['y'], 5)

    def test_if_statement(self):
        self.assertEqual(self.eval('if (2 + 2 == 4) 3;'), js.Completion(js.NORMAL, 3, js.EMPTY))
        self.assertEqual(self.eval('if (false) 3;'), js.EMPTY_COMPLETION)

    def test_if_else_statement(self):
        self.assertEqual(self.eval('if (false) 3; else 5;'), js.Completion(js.NORMAL, 5, js.EMPTY))
        
    def test_dangling_else(self):
        stmt = """if (false)
                       if (true) 3;
                       else 5;"""
        self.assertEqual(self.eval(stmt), js.EMPTY_COMPLETION)

        stmt = """if (true)
                      if (true) 3;
                      else 5;"""
        self.assertEqual(self.eval(stmt), js.Completion(js.NORMAL, 3, js.EMPTY))

    def test_do_while_statement(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval('do ++x; while (x < 3);', context), js.Completion(js.NORMAL, 4, js.EMPTY))
        self.assertEqual(context['x'], 4)

    def test_while_statement(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval('while (x < 5) ++x;', context), js.Completion(js.NORMAL, 5, js.EMPTY))
        self.assertEqual(context['x'], 5)

        
