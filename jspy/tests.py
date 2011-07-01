import unittest2
from jspy.parser import Parser
from jspy import ast, js


class TestParseExpression(unittest2.TestCase):
    def test_primary(self):
        parser = Parser(start='expression')
        self.assertEqual(parser.parse('{7: [9, 10, "ala ma kota"], "ala ma kota": {3: 4}}'),
                         ast.ObjectLiteral(items={7: ast.ArrayLiteral(items=[
                            ast.Literal(value=9), ast.Literal(value=10), ast.Literal(value='ala ma kota')]),
                                                  'ala ma kota': ast.ObjectLiteral(items={3: 4})}))

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
