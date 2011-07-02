"""Module containing basic JavaScript types and objects."""
from collections import namedtuple
import sys


UNDEFINED = object()
EMPTY = object()
NORMAL = object()
BREAK = object()
CONTINUE = object()
RETURN = object()
THROW = object()

# Completion specification type as defined in [ECMA-262 8.9]
Completion = namedtuple('Completion', 'type value target')

EMPTY_COMPLETION = Completion(NORMAL, EMPTY, EMPTY)


def is_abrupt(completion):
    return completion.type is not NORMAL


class Object(object):
    """JavaScript Object as defined in [ECMA-262 8.6]."""
    def __init__(self, items=None):
        if items is None:
            items = {}
        self.d = items

    def __getitem__(self, name):
        return self.d[str(name)]

    def __setitem__(self, name, value):
        self.d[str(name)] = value

    def get(self, name):
        try:
            return self.d[str(name)]
        except KeyError:
            return UNDEFINED
    
    def get_binding_value(self, name):
        return self[name]

    def set_mutable_binding(self, name, value):
        self[name] = value

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.d)

    def __eq__(self, other):
        return self.d == other.d

    
class Array(Object):
    """JavaScript Array as defined in [ECMA-262 15.4]."""
    max_repr_len = 23
    
    def __init__(self, items=None):
        if items is None:
            items = []
        super(Array, self).__init__()
        for i, item in enumerate(items):
            self[float(i)] = item

    def __repr__(self):
        items = list(sorted((int(float(key)), value) for key, value in self.d.items()))
        max_key = items[-1][0] if len(items) > 0 else -1
        shown_items = [self.get(float(i)) for i in range(0, min(max_key, self.max_repr_len) + 1)]
        return 'Array(%r)' % shown_items

    def __str__(self):
        items = list(sorted((int(float(key)), value) for key, value in self.d.items()))
        max_key = items[-1][0] if len(items) > 0 else -1
        shown_items = [self.get(float(i)) for i in range(0, min(max_key, self.max_repr_len) + 1)]
        return '[%s]' % ', '.join(str(item) for item in shown_items)


class Function(object):
    """Function object as defined in [ECMA-262 15.3].

    Algorithm for creating Function objects is in [ECMA-262 13.2]."""
    def __init__(self, parameters, body, scope):
        self.parameters = parameters
        self.body = body
        self.scope = scope
        self.declared_vars = body.get_declared_vars()
    
    def call(self, this, args):
        """Internal [[Call]] method of Function object.

        See [ECMA-262 13.2.1] for a basic algorithm."""
        function_context = self.prepare_function_context(args)
        result = self.body.eval(function_context)
        if result.type is RETURN:
            return result.value
        else:
            # No return statement in function
            return UNDEFINED

    def prepare_function_context(self, args):
        local_vars_dict = dict((name, UNDEFINED) for name in self.declared_vars)
        local_vars_dict.update(self.prepare_args_dict(args))
        return ExecutionContext(local_vars_dict, parent=self.scope)

    def prepare_args_dict(self, args):
        result = {'arguments': args}
        for name in self.parameters:
            result[name] = UNDEFINED
        for name, value in zip(self.parameters, args):
            result[name] = value
        return result

    def __repr__(self):
        return 'Function(parameters=%r, body=%r, scope=%r)' % (self.parameters,
                                                               self.body,
                                                               self.scope)


class NativeFunction(object):
    """Function implemented in Python, callable from JavaScript code."""
    def __init__(self, f):
        self.f = f

    def call(self, this, args):
        return self.f(this, args)

    def __repr__(self):
        return 'NativeFunction(f=%r)' % (self.f)


class Console(Object):
    """Global `console` object, behaving similar to Firebug's one."""
    def __init__(self, out=None):
        self.out = out if out is not None else sys.stdout
        self.d = {'log': NativeFunction(self.log)}

    def log(self, this, args):
        self.out.write(' '.join(str(arg) for arg in args))
        self.out.write('\n')


class ReferenceError(RuntimeError):
    pass


class ExecutionContext(object):
    def __init__(self, env, parent=None):
        assert isinstance(env, dict)
        self.env = env
        self.parent = parent

    def __getitem__(self, name):
        try:
            return self.env[name]
        except KeyError:
            if self.parent is None:
                raise ReferenceError('Reference %r not found in %r' % (name, self))
            return self.parent[name]

    def __setitem__(self, name, value):
        self.env[name] = value
    
    def get_binding_value(self, name):
        return self[name]
    
    def set_mutable_binding(self, name, value):
        if name not in self.env:
            if self.parent is None:
                # XXX: Should I support strict or non-strict mode?
                # raise ReferenceError("%r is not declared" % name)
                self.env[name] = value
            else:
                self.parent.set_mutable_binding(name, value)
        else:
            self.env[name] = value

    def get_this_reference(self):
        return self['this']

    def __repr__(self):
        return 'ExecutionContext(%r, parent=%r)' % (self.env, self.parent)


class Reference(object):
    """JavaScript reference specification type as defined in [ECMA-262 8.7]."""
    def __init__(self, name, base):
        self.name = name
        self.base = base

    def is_unresolvable(self):
        return self.base is UNDEFINED

    def has_primitive_base(self):
        return isinstance(self.base, (basestring, float, bool))

    def is_property(self):
        return isinstance(self.base, Object) or self.has_primitive_base()

    def get_value(self):
        if self.is_unresolvable():
            raise ReferenceError("%r is unresolvable" % self)
        return self.base.get_binding_value(self.name)

    def put_value(self, value):
        if self.is_unresolvable():
            raise ReferenceError("%r is unresolvable" % value)
        self.base.set_mutable_binding(self.name, value)
    
    def __repr__(self):
        return 'Reference(%r, %r)' % (self.name, self.base)


def get_value(obj):
    """Returns a value of `obj`, resolving a reference if needed.
    
    See [ECMA-262 8.7.1] for details."""
    if isinstance(obj, Reference):
        return obj.get_value()
    else:
        return obj


def put_value(obj, value):
    """Sets the value of `obj` reference to `value`.

    See [ECMA-262 8.7.2] for details."""
    if isinstance(obj, Reference):
        obj.put_value(value)
    else:
        raise ReferenceError("Can't put a value of non-reference object %r" % obj)
