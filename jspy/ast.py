import sys


class JSArray(object):
    def __init__(self, items):
        self.items = items


class JSObject(object):
    def __init__(self, items):
        self.items = items


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
        return context['this']


class Identifier(Node):
    arguments = ['name']

    def eval(self, context):
        return context[self.name]


class Literal(Node):
    arguments = ['value']

    def eval(self, context):
        return self.value


class ArrayLiteral(Node):
    children = ['items']

    def eval(self, context):
        return JSArray(items=[item.eval(context) for item in self.items])


class ObjectLiteral(Node):
    children = ['items']

    def eval(self, context):
        return JSObject(items=[item.eval(context) for item in self.items])


class PropertyAccessor(Node):
    children = ['obj', 'key']

    def eval(self, context):
        return self.obj.eval(context)[self.key.eval(context)]


class Constructor(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        return JSObject()


class FunctionCall(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        return self.obj.eval(context)([argument.eval(context) for argument in self.arguments])


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
            # TODO
            return expression_value
        elif self.op == '--':
            # TODO
            return expression_value
        elif self.op == '+':
            return expression_value
        elif self.op == '-':
            return -expression_value
        elif self.op == '~':
            return ~expression_value
        elif self.op == '!':
            return not expression_value
        else:
            raise SyntaxError('Unknown unary operand: %s' % self.op)


class BinaryOp(Node):
    arguments = ['op']
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        left = self.left_expression.eval(context)
        right = self.right_expression.eval(context)
        if self.op == '*':
            return left * right
        elif self.op == '/':
            return left / right
        elif self.op == '%':
            return left % right
        elif self.op == '+':
            return left + right
        elif self.op == '-':
            return left + right
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
            raise SyntaxError('Unknown binary operand: %s' % self.op)


class ConditionalOp(Node):
    children = ['condition', 'true_expression', 'false_expression']

    def eval(self, context):
        condition_value = self.condition.eval(context)
        if condition_value:
            return self.true_expression.eval(context)
        else:
            return self.false_expression.eval(context)


class Assignment(Node):
    arguments = ['op']
    children = ['reference', 'expression']

    def eval(self, context):
        # TODO
        return self.expression.eval(context)


class MultiExpression(Node):
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        self.left_expression.eval(context)
        return self.right_expression.eval(context)

