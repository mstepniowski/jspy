import sys


UNDEFINED = object()


class ReferenceError(RuntimeError):
    pass


class ExecutionContext(dict):
    def get_binding_value(self, name):
        return self[name]

    def set_mutable_binding(self, name, value):
        if name not in self:
            raise ReferenceError("%r is not declared")
        self[name] = value

    def get_this_reference(self):
        return self['this']


class JSReference(object):
    """JavaScript reference type as defined in [ECMA-262 8.7]."""
    def __init__(self, name, base):
        self.name = name
        self.base = base

    def is_unresolvable(self):
        return self.base is UNDEFINED

    def has_primitive_base(self):
        return isinstance(self.base, (basestring, float, bool))

    def is_property(self):
        return isinstance(self.base, JSObject) or self.has_primitive_base()

    def __repr__(self):
        return 'Reference(%r, %r)' % (self.name, self.base)


def get_value(obj):
    """Returns a value of `obj`, resolving a reference if needed.
    
    See [ECMA-262 8.7.1] for details."""
    if not isinstance(obj, JSReference):
        return obj
    if obj.is_unresolvable():
        raise ReferenceError("%r is unresolvable" % obj)
    if obj.is_property():
        raise NotImplementedError("Object references are not supported: %r" % obj)
    else:
        # `obj.base` must be an `ExecutionContext` at this point
        return obj.base.get_binding_value(obj.name)


def put_value(obj, value):
    """Sets the value of `obj` reference to `value`.

    See [ECMA-262 8.7.2] for details."""
    if not isinstance(obj, JSReference):
        raise ReferenceError("Can't put a value of non-reference object %r" % obj)
    if obj.is_unresolvable():
        raise ReferenceError("%r is unresolvable" % obj)
    if obj.is_property():
        # TODO
        raise NotImplementedError("Object references are not supported: %r" % obj)
    else:
        # `obj.base` must be an `ExecutionContext` at this point
        obj.base.set_mutable_binding(obj.name, value)


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
        return context.get_this_reference()


class Identifier(Node):
    arguments = ['name']

    def eval(self, context):
        return JSReference(self.name, context)


class Literal(Node):
    arguments = ['value']

    def eval(self, context):
        return self.value


class ArrayLiteral(Node):
    children = ['items']

    def eval(self, context):
        # TODO: Ellision
        return JSArray(items=[get_value(item.eval(context)) for item in self.items])


class ObjectLiteral(Node):
    children = ['items']

    def eval(self, context):
        return JSObject(items=[get_value(item.eval(context)) for item in self.items])


class PropertyAccessor(Node):
    children = ['obj', 'key']

    def eval(self, context):
        base = get_value(self.obj.eval(context))
        return base[get_value(self.key.eval(context))]


class Constructor(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        # TODO
        return JSObject()


class FunctionCall(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        # TODO
        f = get_value(self.obj.eval(context))
        return f([get_value(argument.eval(context)) for argument in self.arguments])


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
            new_value = get_value(expression_value) + 1
            put_value(expression_value, new_value)
            return new_value
        elif self.op == '--':
            new_value = get_value(expression_value) - 1
            put_value(expression_value, new_value)
            return new_value
        elif self.op == 'postfix++':
            old_value = get_value(expression_value)
            put_value(expression_value, old_value + 1)
            return old_value
        elif self.op == 'postfix--':
            old_value = get_value(expression_value)
            put_value(expression_value, old_value - 1)
            return old_value            
        elif self.op == '+':
            return +get_value(expression_value)
        elif self.op == '-':
            return -get_value(expression_value)
        elif self.op == '~':
            return ~get_value(expression_value)
        elif self.op == '!':
            return not get_value(expression_value)
        else:
            raise SyntaxError('Unknown unary operand: %s' % self.op)


class BinaryOp(Node):
    arguments = ['op']
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        left = get_value(self.left_expression.eval(context))
        right = get_value(self.right_expression.eval(context))
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
        condition_value = get_value(self.condition.eval(context))
        if condition_value:
            return get_value(self.true_expression.eval(context))
        else:
            return get_value(self.false_expression.eval(context))


class Assignment(Node):
    arguments = ['op']
    children = ['reference', 'expression']

    def eval(self, context):
        ref = self.reference.eval(context)
        value = get_value(self.expression.eval(context))
        if self.op == '=':
            put_value(ref, value)
            return value
        else:
            new_value = perform_binary_op(self.op[:-1],
                                          get_value(ref),
                                          value)
            put_value(ref, new_value)
            return new_value


class MultiExpression(Node):
    children = ['left_expression', 'right_expression']

    def eval(self, context):
        self.left_expression.eval(context)
        return self.right_expression.eval(context)

