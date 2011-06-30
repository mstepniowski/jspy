import unittest2
from jspy.parser import Parser
from jspy import ast


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


class TestEvalExpression(unittest2.TestCase):
    def eval_expression(self, expression, context=None):
        if context is None:
            context = {}
        expression_ast = Parser(start='expression').parse(expression)
        return expression_ast.eval(context)
    
    def test_binary_op(self):
        self.assertEqual(self.eval_expression('1 + 2 * 7'), 15)

    def test_unary_op(self):
        self.assertEqual(self.eval_expression('+-1'), -1)

    def test_parens(self):
        self.assertEqual(self.eval_expression('(1 + 2) * 7'), 21)

    def test_reference(self):
        self.assertEqual(self.eval_expression('x + 1', {'x': 5}), 6)
