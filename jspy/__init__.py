from jspy.parser import Parser
from jspy.js import ExecutionContext, UNDEFINED


def eval_file(f):
    file_contents = f.read()
    program = Parser().parse(file_contents)
    context = ExecutionContext(dict((name, UNDEFINED) for name in program.get_declared_vars()))
    result = program.eval(context)
    return result.value, context


__version__ = '1.0'
