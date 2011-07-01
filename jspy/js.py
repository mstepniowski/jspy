"""Module containing basic JavaScript types and objects."""
from collections import namedtuple


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
    def __init__(self, items):
        self.items = items


class Array(object):
    def __init__(self, items):
        self.items = items


class Function(object):
    """Function object as defined in [ECMA-262 15.3].

    Algorithm for creating Function objects is in [ECMA-262 13.2]."""
    def __init__(self, parameters, body, scope):
        self.parameters = parameters
        self.body = body
        self.scope = scope

    def call(self, this, args):
        """Internal [[Call]] method of Function object.

        See [ECMA-262 13.2.1] for a basic algorithm."""
        function_context = ExecutionContext(self.prepare_arg_dict(args),
                                            parent=self.scope)
        result = self.body.eval(function_context)
        if result.type is RETURN:
            return result.value
        else:
            # No return statement in function
            return UNDEFINED

    def prepare_arg_dict(self, args):
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


class ReferenceError(RuntimeError):
    pass


class ExecutionContext(object):
    def __init__(self, env, parent=None):
        assert isinstance(env, dict)
        self.env = env
        self.parent = parent

    def __getitem__(self, name):
        return self.env[name]

    def __setitem__(self, name, value):
        self.env[name] = value
    
    def get_binding_value(self, name):
        try:
            return self.env[name]
        except KeyError:
            raise ReferenceError('Reference %r not found in %r' % (name, self))
    
    def set_mutable_binding(self, name, value):
        # TODO: Reenable this after adding support for nested contexts
        # if name not in self:
        #     raise ReferenceError("%r is not declared")
        self[name] = value

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

    def __repr__(self):
        return 'Reference(%r, %r)' % (self.name, self.base)



def get_value(obj):
    """Returns a value of `obj`, resolving a reference if needed.
    
    See [ECMA-262 8.7.1] for details."""
    if not isinstance(obj, Reference):
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
    if not isinstance(obj, Reference):
        raise ReferenceError("Can't put a value of non-reference object %r" % obj)
    if obj.is_unresolvable():
        raise ReferenceError("%r is unresolvable" % obj)
    if obj.is_property():
        # TODO
        raise NotImplementedError("Object references are not supported: %r" % obj)
    else:
        # `obj.base` must be an `ExecutionContext` at this point
        obj.base.set_mutable_binding(obj.name, value)
