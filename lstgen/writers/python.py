"""
Python writer
"""
import ast
from .. import (
    prepare_expr,
    parse_eval_stmt,
    parse_condition_stmt
)
from .base import Writer
from .. import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)

BIG_DECIMAL = '''

class BigDecimal(decimal.Decimal):
    """ Compatibility class for decimal.Decimal """

    ROUND_DOWN = decimal.ROUND_DOWN
    ROUND_UP = decimal.ROUND_UP

    def divide(self, other, scale=None, rounding=None):
        if not scale and not rounding:
            return BigDecimal(self / other)
        if type(scale) is not int:
            raise ValueError("Expected integer value for scale")
        return BigDecimal((self / other)._rescale(-scale, rounding))

    @classmethod
    def valueOf(cls, value):
        return cls(value)

    def multiply(self, other):
        return BigDecimal(self * other)

    def setScale(self, scale, rounding):
        return BigDecimal(self._rescale(-scale, rounding))

    def add(self, other):
        return BigDecimal(self + other)

    def subtract(self, other):
        return BigDecimal(self - other)

    def longValue(self):
        return int(self)

    def compareTo(self, other):
        return BigDecimal(self.compare(other))

BigDecimal.ZERO = BigDecimal(0)
BigDecimal.ONE = BigDecimal(1)
BigDecimal.TEN = BigDecimal(10)

'''

class PythonWriter(Writer):
    """ Python Writer """

    def __init__(self, parser, outfile, class_name=None, indent='    '):
        super(PythonWriter, self).__init__(outfile, indent)
        self.parser = parser
        self.class_name = class_name

    def _write_preamble(self):
        self.writeln("# coding: utf-8")
        self.nl()
        self.writeln("import decimal")
        self.writeln(BIG_DECIMAL)
        self.nl()

    def generate(self):
        class_name = self.class_name if self.class_name else self.parser.internal_name
        self._write_preamble()
        self.writeln('class {}:'.format(class_name))
        with self.indent():
            for const in self.parser.constants:
                value = const.value
                if const.type.endswith('[]'):
                    value = '[{}]'.format(value[1:-1])
                converted = convert_to_python(value)
                self.writeln('{const.name} = {converted}'.format(
                    const=const, converted=converted
                ))
                if const.comment is not None:
                    self._write_comment(const.comment, False)
                    self.nl()
            self._write_constructor()
            # create setters for input vars
            for var in self.parser.input_vars:
                self.nl()
                self.writeln('def set{}(self, value):'.format(var.name.capitalize()))
                with self.indent():
                    if var.type == 'BigDecimal':
                        self.writeln('self.{} = BigDecimal(value)'.format(var.name))
                    else:
                        self.writeln('self.{} = value'.format(var.name))

            # create getters for output vars
            for var in self.parser.output_vars:
                self.nl()
                self.writeln('def get{}(self):'.format(var.name.capitalize()))
                with self.indent():
                    self.writeln('return self.{}'.format(var.name))
            self._write_method(self.parser.main_method)
            for method in self.parser.methods:
                self._write_method(method)

    def _write_constructor(self):
        self.nl()
        self.writeln('def __init__(self, **kwargs):')
        with self.indent():
            # initialize variables with default values
            for (variables, comment, is_input) in [
                    (self.parser.input_vars, 'input variables', True),
                    (self.parser.output_vars, 'output variables', False),
                    (self.parser.internal_vars, 'internal variables', False),
                ]:
                self.writeln('# ' + comment)
                for var in variables:
                    if var.comment is not None:
                        self.nl()
                        self._write_comment(var.comment, True)
                    self.writeln('self.{name} = {value}'.format(
                        name=var.name,
                        value=convert_to_python(var.default)
                    ))
                    if is_input:
                        self.writeln('if "{}" in kwargs:'.format(var.name))
                        with self.indent():
                            self.writeln('self.set{cap}(kwargs["{name}"])'.format(
                                cap=var.name.capitalize(),
                                name=var.name
                            ))
                self.nl()

    def _write_method(self, method):
        self.nl()
        self.writeln('def {}(self):'.format(method.name))
        # actual method body
        with self.indent():
            if method.comment:
                self._write_comment(method.comment, False)
            self._write_stmt_body(method)

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writeln('"""')
        prefix = '# ' if simple else ''
        for line in lines:
            self.writeln('{}{}'.format(prefix, line.strip()))
        if not simple:
            self.writeln('"""')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writeln('self.{}()'.format(part.method_name))
            elif isinstance(part, IfStmt):
                self._write_if(part)
            elif isinstance(part, ElseStmt):
                self._write_else(part)
            elif isinstance(part, ThenStmt):
                self._write_stmt_body(part)

    def _write_if(self, stmt):
        converted = self._convert_if(stmt.condition)
        self.writeln('if {}:'.format(converted))
        with self.indent():
            self._write_stmt_body(stmt)

    def _write_else(self, stmt):
        if not stmt.body:
            # avoid empty else stmts
            return
        self.dec_indent()
        self.writeln('else:')
        self.inc_indent()
        self._write_stmt_body(stmt)

    def _convert_exec(self, expr):
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['self.', var, ' = ']
        ret += astnode_to_python(parsed_stmt)
        return ''.join(ret)

    def _convert_if(self, expr):
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(astnode_to_python(compare_stmt))

def convert_to_python(value):
    """ Convert a java-like expression to valid python code """
    tree = ast.parse(prepare_expr(value))
    node = tree.body[0].value
    return ''.join(astnode_to_python(node))

def astnode_to_python(node):
    """ Convert an AST node to its PHP representation """
    if isinstance(node, ast.Attribute):
        return astnode_to_python(node.value) + ['.', node.attr]
    if isinstance(node, ast.BinOp):
        return (
            astnode_to_python(node.left) +
            astnode_to_python(node.op) +
            astnode_to_python(node.right)
        )
    if isinstance(node, ast.Name):
        if node.id == 'BigDecimal':
            return [node.id]
        elif node.id == 'BigDecimalConstructor':
            return ['BigDecimal']
        return ['self.{}'.format(node.id)]
    if isinstance(node, ast.Add):
        return [' + ']
    if isinstance(node, ast.Sub):
        return [' - ']
    if isinstance(node, ast.Num):
        return [str(node.n)]
    if isinstance(node, ast.BoolOp):
        vals = []
        op = ' and '
        if isinstance(node.op, ast.Or):
            op = ' or '
        for (idx, val) in enumerate(node.values):
            vals += astnode_to_python(val)
            if idx != len(node.values) - 1:
                vals.append(op)
        return vals
    if isinstance(node, ast.UnaryOp):
        op = '-'
        if isinstance(node.op, ast.UAdd):
            op = '+'
        return [op] + astnode_to_python(node.operand)
    if isinstance(node, ast.Subscript):
        return (
            astnode_to_python(node.value) +
            ['['] +
            astnode_to_python(node.slice.value) +
            [']']
        )
    if isinstance(node, ast.Call):
        args = []
        caller = astnode_to_python(node.func)
        for (idx, arg) in enumerate(node.args):
            args += astnode_to_python(arg)
            if idx != len(node.args) - 1:
                args.append(', ')
        return caller + ['('] + args + [')']
    if isinstance(node, ast.List):
        ret = ['[']
        for (idx, elt) in enumerate(node.elts):
            ret += astnode_to_python(elt)
            if idx != len(node.elts) - 1:
                ret.append(', ')
        ret.append(']')
        return ret
    if isinstance(node, ast.Compare):
        return (
            astnode_to_python(node.left) +
            astnode_to_python(node.ops[0]) +
            astnode_to_python(node.comparators[0])
        )
    if isinstance(node, ast.Lt):
        return [' < ']
    if isinstance(node, ast.LtE):
        return [' =< ']
    if isinstance(node, ast.Eq):
        return [' == ']
    if isinstance(node, ast.Gt):
        return [' > ']
    if isinstance(node, ast.GtE):
        return [' >= ']
    if isinstance(node, ast.NotEq):
        return [' != ']
    if isinstance(node, ast.Mult):
        return [' * ']
    if isinstance(node, ast.Div):
        return [' / ']
    raise ValueError("Unknown AST element: {}".format(node))
