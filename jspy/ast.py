from jspy import js


def set_union(sets):
    result = set()
    for s in sets:
        result.update(s)
    return result


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

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return (self.arguments == other.arguments and self.children == other.children
                and all(getattr(self, name) == getattr(other, name) for name in self.arguments)
                and all(getattr(self, name) == getattr(other, name) for name in self.children))

    def __repr__(self):
        kwargs = {}
        for name in self.arguments:
            kwargs[name] = getattr(self, name)
        for name in self.children:
            kwargs[name] = getattr(self, name)
        kwargs_repr = ', '.join('%s=%r' % (name, value) for name, value in kwargs.items())
        return '%s(%s)' % (self.__class__.__name__, kwargs_repr)

    def eval(self, context):
        """Evaluate the expression (possibly modifying context) and return its value."""
        raise NotImplementedError()

    def get_declared_vars(self):
        """Return a set of all variables declared in this scope.

        JavaScript has only function scopes."""
        return set()


#
# Expressions
#
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
        items = [self.get_item_value(item, context) for item in self.items]
        # Elision: remove last item if it's undefined
        if len(items) > 0  and items[-1] is js.UNDEFINED:
            items.pop()
        return js.Array(items=items)

    def get_item_value(self, item, context):
        return js.get_value(item.eval(context)) if item is not None else js.UNDEFINED


class ObjectLiteral(Node):
    children = ['items']

    def eval(self, context):
        items = dict((name, js.get_value(e.eval(context))) for name, e in self.items.items())
        return js.Object(items=items)


class PropertyAccess(Node):
    children = ['obj', 'key']

    def eval(self, context):
        base_value = js.get_value(self.obj.eval(context))
        property_name_value = js.get_value(self.key.eval(context))
        return js.Reference(name=property_name_value, base=base_value)


class Constructor(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        # TODO
        return js.Object()


class FunctionCall(Node):
    children = ['obj', 'arguments']

    def eval(self, context):
        f = js.get_value(self.obj.eval(context))
        return f.call(None, [js.get_value(argument.eval(context)) for argument in self.arguments])


class UnaryOp(Node):
    arguments = ['op']
    children = ['expression']

    def eval(self, context):
        expr = self.expression.eval(context)
        value = js.get_value(expr)
        
        if self.op == 'delete':
            # TODO
            return True
        elif self.op == 'void':
            return js.UNDEFINED
        elif self.op == 'typeof':
            # TODO
            return 'object'
        elif self.op == '++':
            new_value = value + 1
            js.put_value(expr, new_value)
            return new_value
        elif self.op == '--':
            new_value = value - 1
            js.put_value(expr, new_value)
            return new_value
        elif self.op == 'postfix++':
            old_value = value
            js.put_value(expr, old_value + 1)
            return old_value
        elif self.op == 'postfix--':
            old_value = value
            js.put_value(expr, old_value - 1)
            return old_value           
        elif self.op == '+':
            return +value
        elif self.op == '-':
            return -value
        elif self.op == '~':
            return ~value
        elif self.op == '!':
            return not value
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


#
# Statements
#
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

    def get_declared_vars(self):
        return set_union(s.get_declared_vars() for s in self.statements)


class VariableDeclarationList(Node):
    children = ['declarations']

    def eval(self, context):
        for declaration in self.declarations:
            declaration.eval(context)
        return js.EMPTY_COMPLETION

    def get_declared_vars(self):
        return set_union(d.get_declared_vars() for d in self.declarations)


class VariableDeclaration(Node):
    children = ['identifier', 'initialiser']

    def eval(self, context):
        ref = self.identifier.eval(context)
        value = js.get_value(self.initialiser.eval(context))
        js.put_value(ref, value)
        return js.Completion(js.NORMAL, ref.name, js.EMPTY)

    def get_declared_vars(self):
        return set([self.identifier.name])


class EmptyStatement(Node):
    def eval(self, context):
        return js.EMPTY_COMPLETION


class ExpressionStatement(Node):
    children = ['expression']

    def eval(self, context):
        return js.Completion(js.NORMAL,
                             js.get_value(self.expression.eval(context)),
                             js.EMPTY)


class IfStatement(Node):
    children = ['condition', 'true_statement', 'false_statement']

    def eval(self, context):
        condition_value = js.get_value(self.condition.eval(context))
        if condition_value:
            return self.true_statement.eval(context)
        else:
            return self.false_statement.eval(context)

    def get_declared_vars(self):
        return set_union([self.true_statement.get_declared_vars(),
                          self.false_statement.get_declared_vars()])


class WhileStatement(Node):
    children = ['condition', 'statement']

    def eval(self, context):
        result_value = js.EMPTY
        while True:
            condition_value = js.get_value(self.condition.eval(context))
            if not condition_value:
                return js.Completion(js.NORMAL, result_value, js.EMPTY)
            stmt = self.statement.eval(context)
            if stmt.value is not js.EMPTY:
                result_value = stmt.value
            if stmt.type is js.BREAK:
                return js.Completion(js.NORMAL, result_value, js.EMPTY)
            elif js.is_abrupt(stmt) and stmt.type is not js.CONTINUE:
                return stmt

    def get_declared_vars(self):
        return self.statement.get_declared_vars()


class DoWhileStatement(Node):
    children = ['condition', 'statement']

    def eval(self, context):
        result_value = js.EMPTY
        iterating = True
        while iterating:
            stmt = self.statement.eval(context)
            if stmt.value is not js.EMPTY:
                result_value = stmt.value
            if stmt.type is js.BREAK:
                return js.Completion(js.NORMAL, result_value, js.EMPTY)
            elif js.is_abrupt(stmt) and stmt.type is not js.CONTINUE:
                return stmt
            iterating = js.get_value(self.condition.eval(context))
        
        return js.Completion(js.NORMAL, result_value, js.EMPTY)

    def get_declared_vars(self):
        return self.statement.get_declared_vars()


class ContinueStatement(Node):
    def eval(self, context):
        return js.Completion(js.CONTINUE, js.EMPTY, js.EMPTY)


class BreakStatement(Node):
    def eval(self, context):
        return js.Completion(js.BREAK, js.EMPTY, js.EMPTY)


class ReturnStatement(Node):
    children = ['expression']
    
    def eval(self, context):
        if self.expression is None:
            return js.Completion(js.RETURN, js.UNDEFINED, js.EMPTY)
        else:
            return js.Completion(js.RETURN,
                                 js.get_value(self.expression.eval(context)),
                                 js.EMPTY)


class DebuggerStatement(Node):
    def eval(self, context):
        # According to [ECMA-262 12.15] this statement should
        # have no observable effect when run
        return js.EMPTY_COMPLETION


#
# Function definitions
#
class FunctionDefinition(Node):
    children = ['parameters', 'body']

    def eval(self, context):
        return js.Function(parameters=self.get_parameter_names(context),
                           body=self.body,
                           scope=context)

    def get_parameter_names(self, context):
        if self.parameters is None:
            return []
        else:
            return [p.eval(context).name for p in self.parameters]
