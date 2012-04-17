import os.path
import sys
from StringIO import StringIO
from jspy.compat import unittest
from jspy.parser import Parser
from jspy import ast, js, eval_file


class TestExpression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = Parser(start='expression')

    def eval(self, expression, context=None):
        if context is None:
            context = js.ExecutionContext({})
        if not isinstance(context, js.ExecutionContext):
            context = js.ExecutionContext(context)
        expression_ast = self.parser.parse(expression)
        return js.get_value(expression_ast.eval(context))

    def test_parse_object_literal(self):
        self.assertEqual(self.parser.parse('{7: [9, 10, "ala ma kota"], "ala ma kota": {3: 4}}'),
                         ast.ObjectLiteral(
                items={7: ast.ArrayLiteral(items=[ast.Literal(value=9),
                                                  ast.Literal(value=10),
                                                  ast.Literal(value='ala ma kota')]),
                       'ala ma kota': ast.ObjectLiteral(items={3: ast.Literal(value=4)})}))

    def test_parse_binary_op(self):
        self.assertEqual(self.parser.parse('1 + 2 * 7'),
                         ast.BinaryOp(op='+',
                                      left_expression=ast.Literal(value=1),
                                      right_expression=ast.BinaryOp(op='*',
                                                                    left_expression=ast.Literal(value=2),
                                                                    right_expression=ast.Literal(value=7))))
    def test_parse_unary_op(self):
        self.assertEqual(self.parser.parse('+-1'),
                         ast.UnaryOp(op='+',
                                     expression=ast.UnaryOp(op='-',
                                                            expression=ast.Literal(value=1))))

    def test_parse_prefix_op(self):
        self.assertEqual(self.parser.parse('++x'),
                         ast.UnaryOp(op='++',
                                     expression=ast.Identifier(name='x')))

    def test_parse_compound_assignment(self):
        self.assertEqual(self.parser.parse('x /= 5 - 2'),
                         ast.Assignment(op='/=',
                                        reference=ast.Identifier(name='x'),
                                        expression=ast.BinaryOp(op='-',
                                                                left_expression=ast.Literal(value=5),
                                                                right_expression=ast.Literal(value=2))))

    def test_parse_function_expression(self):
        self.assertEqual(self.parser.parse('function (x, y) { return x + y; }'),
                         ast.FunctionDefinition(parameters=[ast.Identifier(name='x'),
                                                            ast.Identifier(name='y')],
                                                body=ast.Block(
                    statements=[ast.ReturnStatement(expression=ast.BinaryOp(op='+',
                                                                            left_expression=ast.Identifier(name='x'),
                                                                            right_expression=ast.Identifier(name='y')))])))

    def test_binary_op(self):
        self.assertEqual(self.eval('1 + 2 * 7'), 15)

    def test_binary_op_reference(self):
        self.assertEqual(self.eval('x + y * 3', {'x': 3, 'y': 2}), 9)

    def test_unary_op(self):
        self.assertEqual(self.eval('+-1'), -1)

    def test_parens(self):
        self.assertEqual(self.eval('(1 + 2) * 7'), 21)

    def test_reference(self):
        self.assertEqual(self.eval('x', {'x': 5}), 5)

    def test_condition_op(self):
        self.assertEqual(self.eval('"ham" === "spam" ? "SPAMSPAMSPAM" : "no spam"'), 'no spam')

    def test_prefix_op(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval('++x', context), 4)
        self.assertEqual(context['x'], 4)
        self.assertEqual(self.eval('--x', context), 3)
        self.assertEqual(context['x'], 3)

    def test_postfix_op(self):
        context = js.ExecutionContext({'x': 3})
        self.assertEqual(self.eval('x++', context), 3)
        self.assertEqual(context['x'], 4)
        self.assertEqual(self.eval('x--', context), 4)
        self.assertEqual(context['x'], 3)
        
    def test_assignment(self):
        self.assertEqual(self.eval('x = 7, x', {'x': 5}), 7)

    def test_compound_assignment(self):
        context = js.ExecutionContext({'x': 15})        
        self.assertEqual(self.eval('x /= 5 - 2', context), 5)
        self.assertEqual(context['x'], 5)

    def test_property_access(self):
        self.assertEqual(self.eval('{cheese: 7, ham: 3}.cheese'), 7)
        self.assertEqual(self.eval("{cheese: 7, ham: 3}['ham']"), 3)

    def test_object_set_property(self):
        context = js.ExecutionContext({'x': js.Object({'cheese': 7, 'ham': 3})})
        self.assertEqual(self.eval('x["cheese"] = 4', context), 4)
        self.assertEqual(context['x']['cheese'], 4)

    def test_object_set_new_property(self):
        context = js.ExecutionContext({'x': js.Object({'cheese': 7, 'ham': 3})})
        self.assertEqual(self.eval('x["spam"] = 2', context), 2)
        self.assertEqual(context['x']['spam'], 2)

    def test_array_literal(self):
        self.assertEqual(self.eval('[9, 10, "ala ma kota"]'),
                         js.Array([9, 10, 'ala ma kota']))

    def test_empty_array_literal(self):
        self.assertEqual(self.eval('[]'), js.Array([]))
    
    def test_array_set_index(self):
        context = js.ExecutionContext({'x': js.Array([9, 10, 'ala ma kota'])})
        self.assertEqual(self.eval('x[2] = 11', context), 11)
        self.assertEqual(context['x'], js.Array([9, 10, 11]))

    def test_array_elision(self):
        self.assertEqual(self.eval('[,]'), js.Array([js.UNDEFINED]))
        self.assertEqual(self.eval('[,,]'), js.Array([js.UNDEFINED, js.UNDEFINED]))
        self.assertEqual(self.eval('[,,,]'), js.Array([js.UNDEFINED, js.UNDEFINED, js.UNDEFINED]))
        self.assertEqual(self.eval('[1, 2,]'), js.Array([1, 2]))
        self.assertEqual(self.eval('[1, 2,,]'), js.Array([1, 2, js.UNDEFINED]))
        self.assertEqual(self.eval('[1,,2]'), js.Array([1, js.UNDEFINED, 2]))
        self.assertEqual(self.eval('[1,,,2]'), js.Array([1, js.UNDEFINED, js.UNDEFINED, 2]))


class TestStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = Parser(start='statement')

    def eval(self, stmt, context=None):
        if context is None:
            context = js.ExecutionContext({})
        if not isinstance(context, js.ExecutionContext):
            context = js.ExecutionContext(context)
        stmt_ast = self.parser.parse(stmt)
        return js.get_value(stmt_ast.eval(context))

    def test_parse_block(self):
        self.assertEqual(self.parser.parse('{ 1; 3; }'),
                         ast.Block(statements=[ast.ExpressionStatement(expression=ast.Literal(value=1)),
                                               ast.ExpressionStatement(expression=ast.Literal(value=3))]))
    
    def test_parse_variable_statement(self):
        self.assertEqual(self.parser.parse('var x = 7, y = 5;'),
                         ast.VariableDeclarationList(
                declarations=[ast.VariableDeclaration(identifier=ast.Identifier(name='x'),
                                                      initialiser=ast.Literal(value=7)),
                              ast.VariableDeclaration(identifier=ast.Identifier(name='y'),
                                                      initialiser=ast.Literal(value=5))]))

    def test_parse_variable_statement_without_initialiser(self):
        self.assertEqual(self.parser.parse('var x, y = 5;'),
                         ast.VariableDeclarationList(
                declarations=[ast.VariableDeclaration(identifier=ast.Identifier(name='x'),
                                                      initialiser=None),
                              ast.VariableDeclaration(identifier=ast.Identifier(name='y'),
                                                      initialiser=ast.Literal(value=5))]))

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

    def test_variable_declaration(self):
        context = js.ExecutionContext({})
        self.assertEqual(self.eval('var x = 7;', context), js.EMPTY_COMPLETION)
        self.assertEqual(context['x'], 7)

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

    def test_continue_statement(self):
        stmt = """while (x < 10) {
                      ++x;
                      if (x % 2 == 0)
                          continue;
                      ++y;
               }"""
        context = js.ExecutionContext({'x': 0, 'y': 0})
        self.assertEqual(self.eval(stmt, context), js.Completion(js.NORMAL, 5, js.EMPTY))
        self.assertEqual(context['x'], 10)
        self.assertEqual(context['y'], 5)
  
    def test_break_statement(self):
        stmt = """while (x < 10) {
                      ++x;
                      if (x % 3 == 0)
                          break;
                      ++y;
               }"""
        context = js.ExecutionContext({'x': 0, 'y': 0})
        self.assertEqual(self.eval(stmt, context), js.Completion(js.NORMAL, 2, js.EMPTY))
        self.assertEqual(context['x'], 3)
        self.assertEqual(context['y'], 2)


class TestProgram(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = Parser(start='program')

    def eval(self, expression, context=None):
        if context is None:
            context = js.ExecutionContext({})
        if not isinstance(context, js.ExecutionContext):
            context = js.ExecutionContext(context)
        expression_ast = self.parser.parse(expression)
        return js.get_value(expression_ast.eval(context))

    def test_return_statement(self):
        program = """function () { return 4; 7; } ();"""
        self.assertEqual(self.eval(program), js.Completion(js.NORMAL, 4, js.EMPTY))

    def test_function_as_variable(self):
        program = """var f = function () { return 42; };
                     f();"""
        self.assertEqual(self.eval(program), js.Completion(js.NORMAL, 42, js.EMPTY))

    def test_arguments(self):
        program = """var sqr = function (x) { return x * x; };
                     sqr(7);"""
        self.assertEqual(self.eval(program), js.Completion(js.NORMAL, 49, js.EMPTY))
    
    def test_function_as_argument(self):
        program = """var double = function (f, x) { return f(f(x)); };
                     double(function (x) { return x * x; }, 2);"""
        self.assertEqual(self.eval(program), js.Completion(js.NORMAL, 16, js.EMPTY))

    def test_modify_global_variable(self):
        program = """var x = 1, incrementX = function () { x += 1; };
                     incrementX();
                     incrementX();
                     x;"""
        self.assertEqual(self.eval(program), js.Completion(js.NORMAL, 3, js.EMPTY))
        
    def test_shadowing(self):
        program = """var x = 1;
                     var shadow = function () {
                         var x = 3; x += 1; return x;
                     };
                     shadow();"""
        context = js.ExecutionContext({})
        self.assertEqual(self.eval(program, context), js.Completion(js.NORMAL, 4, js.EMPTY))
        self.assertEqual(context['x'], 1)
        
    def test_closure(self):
        program = """var fibgen = function () {
                         var a = 0, b = 1;
                         return function () {
                             var old = a;
                             a = b;
                             b = b + old;
                             return old;
                         };
                     };

                     var fib = fibgen();
                     var f1 = fib();
                     var f2 = fib();
                     fib(); fib(); fib(); fib();
                     var f7 = fib();
                     fib(); fib(); fib(); fib();

                     var fib2 = fibgen();
                     fib2(); fib2(); fib2(); fib2();
                     var f5 = fib2();

                     fib(); // f12
                  """
        context = js.ExecutionContext({})
        self.assertEqual(self.eval(program, context), js.Completion(js.NORMAL, 89, js.EMPTY))
        self.assertEqual(context['f1'], 0)
        self.assertEqual(context['f2'], 1)
        self.assertEqual(context['f5'], 3)
        self.assertEqual(context['f7'], 8)

    def test_console_object(self):
        program = """var i = 0;
                     while (i < 10) {
                         console.log(i);
                         i++;
                     }
                  """
        out = StringIO()
        context = js.ExecutionContext({'console': js.Console(out=out)})
        self.assertEqual(self.eval(program, context), js.Completion(js.NORMAL, 9, js.EMPTY))
        self.assertEqual(out.getvalue(), "0.0\n1.0\n2.0\n3.0\n4.0\n5.0\n6.0\n7.0\n8.0\n9.0\n")


class TestFile(unittest.TestCase):
    def setUp(self):
        # Patch `sys.stdout` to catch program output
        self.out = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.out

    def tearDown(self):
        sys.stdout = self.old_stdout
    
    def eval(self, file_name):
        package_directory = os.path.dirname(__file__)
        file_path = os.path.join(package_directory, 'test_files', file_name)
        return eval_file(file_path)

    def test_fibgen(self):
        result, context = self.eval('fibgen.js')
        self.assertEqual(context['fibonacciNumbers'],
                         js.Array([0.0, 1.0, 1.0, 2.0, 3.0,
                                   5.0, 8.0, 13.0, 21.0, 34.0,
                                   55.0, 89.0, 144.0, 233.0, 377.0,
                                   610.0, 987.0, 1597.0, 2584.0, 4181.0,
                                   6765.0]))

    def test_primes(self):
        self.eval('primes.js')
        self.assertEqual(self.out.getvalue(),
                         "2.0\n3.0\n5.0\n7.0\n11.0\n13.0\n17.0\n19.0\n23.0\n"
                         "29.0\n31.0\n37.0\n41.0\n43.0\n47.0\n53.0\n59.0\n"
                         "61.0\n67.0\n71.0\n")

    def test_pascal(self):
        self.eval('pascal.js')
        self.assertEqual(self.out.getvalue(), """\
[1.0]
[1.0, 1.0]
[1.0, 2.0, 1.0]
[1.0, 3.0, 3.0, 1.0]
[1.0, 4.0, 6.0, 4.0, 1.0]
[1.0, 5.0, 10.0, 10.0, 5.0, 1.0]
[1.0, 6.0, 15.0, 20.0, 15.0, 6.0, 1.0]
[1.0, 7.0, 21.0, 35.0, 35.0, 21.0, 7.0, 1.0]
[1.0, 8.0, 28.0, 56.0, 70.0, 56.0, 28.0, 8.0, 1.0]
[1.0, 9.0, 36.0, 84.0, 126.0, 126.0, 84.0, 36.0, 9.0, 1.0]
""")

    def test_object_literal(self):
        result, context = self.eval('object_literal.js')
        self.assertEqual(result, js.Object({u'season': js.Object({u'episode': js.Array([js.Object({
                                            u'available': u'true',
                                            u'episodenumber': u'402',
                                            u'description': u'...',
                                            u'tags': u'Tooth Fairy|Cartman|Tits|Kyle|Stan',
                                            u'url': u'http://www.southparkstudios.com/full-episodes/s04e02-the-tooth-fairy-tats',
                                            u'title': u'The Tooth Fairy Tats',
                                            u'when': u'04.05.2000',
                                            u'thumbnail_190': u'http://example.com/episode_thumbnails/s04e02_480.jpg?width=190',
                                            u'id': u'103570',
                                            u'airdate': u'04.05.2000',
                                            u'thumbnail_larger': u'http://example.com/episode_thumbnails/s04e02_480.jpg?width=63',
                                            u'thumbnail': u'http://example.com/episode_thumbnails/s04e02_480.jpg?width=55'})])})}))
