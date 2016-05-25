"""
Java writer
"""
import ast
from .. import (
    prepare_expr,
    parse_eval_stmt,
    parse_condition_stmt
)
from .base import BaseGenerator
from .. import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)

class JavaGenerator(BaseGenerator):
    """ Java Generator """

    instance_var = 'this'
    """ Name of the implicit instance variable (if any) """

    def __init__(self, parser, outfile, class_name=None, indent=None, package_name='default'):
        super(JavaGenerator, self).__init__(parser, outfile, class_name, indent)
        self.package_name = package_name

    def generate(self):
        wr = self.writer
        if self.package_name:
            wr.writeln('package {};'.format(self.package_name))
            wr.nl()
        wr.writeln('import java.math.BigDecimal;')
        wr.nl()
        with self.writer.indent('public class {}'.format(self.class_name)):
            wr.writeln("/* Constants */")
            for const in self.parser.constants:
                if const.comment is not None:
                    wr.nl()
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
                wr.writeln('protected final static {const.type} {const.name} = {converted};'.format(
                    const=const,
                    converted=converted
                ))
            # create input and output vars
            for (comment, variables) in [
                    ('Input variables', self.parser.input_vars),
                    ('Output variables', self.parser.output_vars),
                    ('Internal variables', self.parser.internal_vars),
                ]:
                wr.nl()
                wr.writeln('/* {} */'.format(comment))
                for var in variables:
                    if var.comment is not None:
                        wr.nl()
                        self._write_comment(var.comment, False)
                    wr.writeln('protected {var.type} {var.name} = {var.default};'.format(var=var))
            # create setters for input vars
            for var in self.parser.input_vars:
                wr.nl()
                signature = 'public void set{cap}({type} value)'.format(
                    cap=var.name.capitalize(),
                    type=var.type
                )
                with wr.indent(signature):
                    wr.writeln('this.{} = value;'.format(var.name))

            # create getters for output vars
            for var in self.parser.output_vars:
                wr.nl()
                signature = 'public {type} get{cap}()'.format(
                    cap=var.name.capitalize(),
                    type=var.type
                )
                with wr.indent(signature):
                    wr.writeln('return this.{};'.format(var.name))
            self._write_method(self.parser.main_method, 'public')
            for method in self.parser.methods:
                self._write_method(method)
        wr.nl()

    def _write_method(self, method, visibility='protected'):
        self.writer.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        signature = '{visibility} void {name}()'.format(
            visibility=visibility,
            name=method.name
        )
        # actual method body
        with self.writer.indent(signature):
            self._write_stmt_body(method)

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writer.writeln('/**')
        prefix = '// ' if simple else ' * '
        for line in lines:
            self.writer.writeln(u'{}{}'.format(prefix, line.strip()))
        if not simple:
            self.writer.writeln(' */')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writer.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writer.writeln('this.{}();'.format(part.method_name))
            elif isinstance(part, IfStmt):
                self._write_if(part)
            elif isinstance(part, ElseStmt):
                self._write_else(part)
            elif isinstance(part, ThenStmt):
                self._write_stmt_body(part)

    def _write_if(self, stmt):
        converted = self._convert_if(stmt.condition)
        with self.writer.indent('if ({})'.format(converted)):
            self._write_stmt_body(stmt)

    def _write_else(self, stmt):
        if not stmt.body:
            # avoid empty else stmts
            return
        self.writer.dec_indent()
        self.writer.writeln('} else {')
        self.writer.inc_indent()
        self._write_stmt_body(stmt)

    def _convert_exec(self, expr):
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['this.', var, ' = ']
        ret += self.to_code(parsed_stmt)
        ret.append(';')
        return ''.join(ret)

    def _convert_if(self, expr):
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(self.to_code(compare_stmt))

    def convert_to_java(self, value):
        """ Converts java pseudo code into valid java code """
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.to_code(node))
