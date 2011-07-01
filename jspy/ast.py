import sys
from jspy import js


def perform_binary_op(op, left, right):
    if op == '*':
        return left * right
    elif op == '/':
        return left / right
    elif op == '%':
        return left % right
    elif op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '<<':
        return left << right
    elif op == '>>':
        return left >> right
    elif op == '&':
        return left & right
    elif op == '^':
        return left ^ right
    elif op == '|':
        return left | right
    else:
        raise ValueError('Unsupported binary operand: %r' % op)


class Node(object):
    """Abstract base class for AST nodes."""
    arguments = []
    children = []
    
    def __init__(self, **kwargs):
        for name in self.arguments:
            setattr(self, name, kwargs.pop(name))
        for name in self.children:
            setattr(self, name, kwargs.pop(name))
        assert len(kwargs) == 0
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.
            
            file:   
                Open IO buffer into which the Node is printed.
            
            offset: 
                Initial offset (amount of leading spaces) 
            
            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.
            
            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        lead = ' ' * offset
        buf.write(lead + self.__class__.__name__+': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for c in self.children():
            c.show(buf, offset + 2, attrnames, showcoord)

    def __eq__(self, other):
        return self.arguments == other.arguments and self.children == other.children


class This(Node):
    """The this keyword evaluates to the value of the ThisBinding of the current execution context."""

    def eval(self, context):
        return context.get_this_reference()


class Identifier(Node):
    arguments = ['name']

    def eval(self, context):
        return js.Reference(self.name, context)


class Literal(Node):
    arguments = ['value']

    def eval(self, context):
        return self.value


class ArrayLiteral(Node):
    children = ['items']

    def eval(self, context):
        # TODO: Ellision
        return js.Array(items=[js.get_value(item.eval(context)) for item in self.items])


class ObjectLiteral(Node):
    children = ['items']

    def eval(self, context):
        return js.Object(items=[js.get_value(item.eval(context)) for item in self.items])


class PropertyAccessor(Node):
    children = ['obj', 'key']

    def eval(self, context):
        base = js.get_value(self.obj.eval(context))
        return base[js.get_value(self.key.eval(context))]


class Constructor(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        # TODO
        return js.Object()


class FunctionCall(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        # TODO
        f = js.get_value(self.obj.eval(context))
        return f([js.get_value(argument.eval(context)) for argument in self.arguments])


class UnaryOp(Node):
    arguments = ['op']
    children = ['expression']

    def eval(self, context):
        expression_value = self.expression.eval(context)
        if self.op == 'delete':
            # TODO
            return True
        elif self.op == 'void':
            # TODO: Some object to represent undefined value
            return 'undefined'
        elif self.op == 'typeof':
            # TODO
            return 'object'
        elif self.op == '++':
            new_value = js.get_value(expression_value) + 1
            js.put_value(expression_value, new_value)
            return new_value
        elif self.op == '--':
            new_value = js.get_value(expression_value) - 1
            js.put_value(expression_value, new_value)
            return new_value
        elif self.op == 'postfix++':
            old_value = js.get_value(expression_value)
            js.put_value(expression_value, old_value + 1)
            return old_value
        elif self.op == 'postfix--':
            old_value = js.get_value(expression_value)
            js.put_value(expression_value, old_value - 1)
            return old_value            
        elif self.op == '+':
            return +js.get_value(expression_value)
        elif self.op == '-':
            return -js.get_value(expression_value)
        elif self.op == '~':
            return ~js.get_value(expression_value)
        elif self.op == '!':
            return not js.get_value(expression_value)
        else:
            raise SyntaxError('Unknown unary operand: %s' % self.op)


class BinaryOp(Node):
    arguments = ['op']
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        left = js.get_value(self.left_expression.eval(context))
        right = js.get_value(self.right_expression.eval(context))
        if self.op == '*':
            return left * right
        elif self.op == '/':
            return left / right
        elif self.op == '%':
            return left % right
        elif self.op == '+':
            return left + right
        elif self.op == '-':
            return left - right
        elif self.op == '<<':
            return left << right
        elif self.op == '>>':
            return left >> right
        elif self.op == '<':
            return left < right
        elif self.op == '<=':
            return left <= right
        elif self.op == '>':
            return left > right
        elif self.op == '>=':
            return left >= right
        elif self.op == 'instanceof':
            # TODO
            return False
        elif self.op == 'in':
            # TODO
            return False
        elif self.op == '==':
            return left == right
        elif self.op == '!=':
            return left != right
        elif self.op == '===':
            return left == right
        elif self.op == '!==':
            return left != right
        elif self.op == '&':
            return left & right
        elif self.op == '^':
            return left ^ right
        elif self.op == '|':
            return left | right
        elif self.op == '&&':
            return left and right
        elif self.op == '||':
            return left or right
        else:
            raise SyntaxError('Unknown binary operand: %r' % self.op)


class ConditionalOp(Node):
    children = ['condition', 'true_expression', 'false_expression']

    def eval(self, context):
        condition_value = js.get_value(self.condition.eval(context))
        if condition_value:
            return js.get_value(self.true_expression.eval(context))
        else:
            return js.get_value(self.false_expression.eval(context))


class Assignment(Node):
    arguments = ['op']
    children = ['reference', 'expression']

    def eval(self, context):
        ref = self.reference.eval(context)
        value = js.get_value(self.expression.eval(context))
        if self.op == '=':
            js.put_value(ref, value)
            return value
        else:
            new_value = perform_binary_op(self.op[:-1],
                                          js.get_value(ref),
                                          value)
            js.put_value(ref, new_value)
            return new_value


class MultiExpression(Node):
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        self.left_expression.eval(context)
        return self.right_expression.eval(context)


class Block(Node):
    children = ['statements']

    def eval(self, context):
        result = js.EMPTY_COMPLETION
        for statement in self.statements:
            partial_result = statement.eval(context)
            if js.is_abrupt(partial_result):
                return partial_result
            # Ignore empty statement values, as specified in [ECMA-262 12.1]
            if partial_result.value is not js.EMPTY:
                result = partial_result
        return result


class VariableDeclarationList(Node):
    children = ['declarations']

    def eval(self, context):
        for declaration in self.declarations:
            declaration.eval(context)
        return js.EMPTY_COMPLETION


class VariableDeclaration(Node):
    children = ['identifier', 'initialiser']

    def eval(self, context):
        ref = self.identifier.eval(context)
        value = js.get_value(self.initialiser.eval(context))
        js.put_value(ref, value)
        return js.Completion(js.NORMAL, ref.name, js.EMPTY)


class EmptyStatement(Node):
    def eval(self, context):
        return js.EMPTY_COMPLETION


class ExpressionStatement(Node):
    children = ['expression']

    def eval(self, context):
        return js.Completion(js.NORMAL,
                             js.get_value(self.expression.eval(context)),
                             js.EMPTY)
