import codecs
from jspy.parser import Parser
from jspy.js import ExecutionContext, UNDEFINED


__version__ = '1.0'


def eval_file(file_name):
    f = codecs.open(file_name, encoding='utf-8')
    file_contents = f.read()
    program = Parser().parse(file_contents)
    context = ExecutionContext(dict((name, UNDEFINED) for name in program.get_declared_vars()))
    result = program.eval(context)
    return result.value, context
