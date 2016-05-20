"""
Java writer
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

class JavaWriter(Writer):
    """ Java Writer """

    def __init__(self, parser, outfile, class_name=None, package_name='default', indent='    '):
        super(JavaWriter, self).__init__(outfile, indent)
        self.parser = parser
        self.class_name = class_name
        self.package_name = package_name
        self.constant_names = set(const.name for const in self.parser.constants)

    def generate(self):
        class_name = self.class_name if self.class_name else self.parser.internal_name
        if class_name != self.class_name:
            self.class_name = class_name
        if self.package_name:
            self.writeln('package {};'.format(self.package_name))
            self.nl()
        self.writeln('import java.math.BigDecimal;')
        self.nl()
        self.writeln('public class {} {{'.format(class_name))
        with self.indent():
            self.writeln("/* Constants */")
            for const in self.parser.constants:
                if const.comment is not None:
                    self.nl()
                    self._write_comment(const.comment, False)
                value = const.value
                is_list_initializer = False
                if const.type.endswith('[]'):
                    value = '[{}]'.format(value[1:-1])
                    is_list_initializer = True
                converted = self.convert_to_java(value)
                if is_list_initializer:
                    # convert python-style list back to java
                    converted = '{{{}}}'.format(converted[1:-1])
                self.writeln('protected final static {const.type} {const.name} = {converted};'.format(
                    const=const,
                    converted=converted
                ))
            # create input and output vars
            for (comment, variables) in [
                    ('Input variables', self.parser.input_vars),
                    ('Output variables', self.parser.output_vars),
                    ('Internal variables', self.parser.internal_vars),
                ]:
                self.nl()
                self.writeln('/* {} */'.format(comment))
                for var in variables:
                    if var.comment is not None:
                        self.nl()
                        self._write_comment(var.comment, False)
                    self.writeln('protected {var.type} {var.name} = {var.default};'.format(var=var))
            # create setters for input vars
            for var in self.parser.input_vars:
                self.nl()
                self.writeln('public void set{cap}({type} value) {{'.format(
                    cap=var.name.capitalize(),
                    type=var.type
                ))
                with self.indent():
                    self.writeln('this.{} = value;'.format(var.name))
                self.writeln('}')

            # create getters for output vars
            for var in self.parser.output_vars:
                self.nl()
                self.writeln('public {type} get{cap}() {{'.format(
                    cap=var.name.capitalize(),
                    type=var.type
                ))
                with self.indent():
                    self.writeln('return this.{};'.format(var.name))
                self.writeln('}')
            self._write_method(self.parser.main_method, 'public')
            for method in self.parser.methods:
                self._write_method(method)
        self.writeln('}')
        self.nl()

    def _write_method(self, method, visibility='protected'):
        self.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        self.writeln('{visibility} void {name}() {{'.format(
            visibility=visibility,
            name=method.name
        ))
        # actual method body
        with self.indent():
            self._write_stmt_body(method)
        self.writeln('}')

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writeln('/**')
        prefix = '// ' if simple else ' * '
        for line in lines:
            self.writeln('{}{}'.format(prefix, line.strip()))
        if not simple:
            self.writeln(' */')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writeln('this.{}();'.format(part.method_name))
            elif isinstance(part, IfStmt):
                self._write_if(part)
            elif isinstance(part, ElseStmt):
                self._write_else(part)
            elif isinstance(part, ThenStmt):
                self._write_stmt_body(part)

    def _write_if(self, stmt):
        converted = self._convert_if(stmt.condition)
        self.writeln('if ({}) {{'.format(converted))
        with self.indent():
            self._write_stmt_body(stmt)
        self.writeln('}')

    def _write_else(self, stmt):
        if not stmt.body:
            # avoid empty else stmts
            return
        self.dec_indent()
        self.writeln('} else {')
        self.inc_indent()
        self._write_stmt_body(stmt)

    def _convert_exec(self, expr):
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['this.', var, ' = ']
        ret += self.astnode_to_java(parsed_stmt)
        ret.append(';')
        return ''.join(ret)

    def _convert_if(self, expr):
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(self.astnode_to_java(compare_stmt))

    def convert_to_java(self, value):
        """ Converts java pseudo code into valid java code """
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.astnode_to_java(node))

    def astnode_to_java(self, node):
        """ convert an AST node to its PHP representation """
        if isinstance(node, ast.Attribute):
            return self.astnode_to_java(node.value) + ['.', node.attr]
        if isinstance(node, ast.BinOp):
            return (
                self.astnode_to_java(node.left) +
                self.astnode_to_java(node.op) +
                self.astnode_to_java(node.right)
            )
        if isinstance(node, ast.Name):
            if node.id == 'BigDecimal':
                return [node.id]
            elif node.id == 'BigDecimalConstructor':
                return ['new BigDecimal']
            if node.id in self.constant_names:
                return ['{}.{}'.format(self.class_name, node.id)]
            return ['this.{}'.format(node.id)]
        if isinstance(node, ast.Add):
            return [' + ']
        if isinstance(node, ast.Sub):
            return [' - ']
        if isinstance(node, ast.Num):
            return [str(node.n)]
        if isinstance(node, ast.BoolOp):
            vals = []
            op = ' && '
            if isinstance(node.op, ast.Or):
                op = ' || '
            for (idx, val) in enumerate(node.values):
                vals += self.astnode_to_java(val)
                if idx != len(node.values) - 1:
                    vals.append(op)
            return vals
        if isinstance(node, ast.UnaryOp):
            op = '-'
            if isinstance(node.op, ast.UAdd):
                op = '+'
            return [op] + self.astnode_to_java(node.operand)
        if isinstance(node, ast.Subscript):
            return (
                self.astnode_to_java(node.value) +
                ['['] +
                self.astnode_to_java(node.slice.value) +
                [']']
            )
        if isinstance(node, ast.Call):
            args = []
            caller = self.astnode_to_java(node.func)
            for (idx, arg) in enumerate(node.args):
                args += self.astnode_to_java(arg)
                if idx != len(node.args) - 1:
                    args.append(', ')
            return caller + ['('] + args + [')']
        if isinstance(node, ast.List):
            ret = ['[']
            for (idx, elt) in enumerate(node.elts):
                ret += self.astnode_to_java(elt)
                if idx != len(node.elts) - 1:
                    ret.append(', ')
            ret.append(']')
            return ret
        if isinstance(node, ast.Compare):
            return (
                self.astnode_to_java(node.left) +
                self.astnode_to_java(node.ops[0]) +
                self.astnode_to_java(node.comparators[0])
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
