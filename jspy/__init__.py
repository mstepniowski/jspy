import codecs
from jspy.parser import Parser
from jspy.js import Console, ExecutionContext, UNDEFINED


__version__ = '1.0'


def create_default_global_objects():
    return {'console': Console()}


def eval_file(file_name, global_objects=None):
    if global_objects is None:
        global_objects = create_default_global_objects()

    # Parse file
    f = codecs.open(file_name, encoding='utf-8')
    file_contents = f.read()
    program = Parser().parse(file_contents)
    declared_vars = dict((name, UNDEFINED) for name in program.get_declared_vars())
    declared_vars.update(global_objects)

    # Create the execution context object
    context = ExecutionContext(declared_vars)

    # Run code
    result = program.eval(context)
    return result.value, context
