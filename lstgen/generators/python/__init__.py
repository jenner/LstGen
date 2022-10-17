# coding: utf-8
"""
Python writer
"""
import ast
import inspect

from ... import (
    prepare_expr,
    parse_eval_stmt,
    parse_condition_stmt,
    remove_size_literal
)
from ..base import BaseGenerator
from ... import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)

from . import bd


class PythonGenerator(BaseGenerator):
    """ Python generator """


    bool_and = 'and'
    """ Boolean AND operator """

    bool_or = 'or'
    """ Boolean OR operator """

    bd_class_constructor = 'BigDecimal'
    """ Override BigDecimal class constructor """

    def __init__(self, parser, outfile, class_name=None, indent=None):
        super(PythonGenerator, self).__init__(
            parser,
            outfile,
            class_name,
            indent,
            block_chars=(':', None)
        )

    def _write_preamble(self):
        self.writer.writeln("# coding: utf-8")
        self.writer.nl()
        self.writer.writeln(inspect.getsource(bd))
        self.writer.nl()

    def generate(self):
        self._write_preamble()
        with self.writer.indent('class {}'.format(self.class_name)):
            for const in self.parser.constants:
                value = const.value
                if const.type.endswith('[]'):
                    value = '[{}]'.format(value[1:-1])
                converted = self.convert_to_python(value)
                self.writer.writeln('{const.name} = {converted}'.format(
                    const=const, converted=converted
                ))
                if const.comment is not None:
                    self._write_comment(const.comment, False)
                    self.writer.nl()
            self._write_constructor()
            # create setters for input vars
            for var in self.parser.input_vars:
                self.writer.nl()
                with self.writer.indent('def set{}(self, value)'.format(var.name.capitalize())):
                    if var.type == 'BigDecimal':
                        self.writer.writeln('self.{} = BigDecimal(value)'.format(var.name))
                    else:
                        self.writer.writeln('self.{} = value'.format(var.name))

            # create getters for output vars
            for var in self.parser.output_vars:
                self.writer.nl()
                with self.writer.indent('def get{}(self)'.format(var.name.capitalize())):
                    self.writer.writeln('return self.{}'.format(var.name))
            self._write_method(self.parser.main_method)
            for method in self.parser.methods:
                self._write_method(method)

    def _write_constructor(self):
        self.writer.nl()
        with self.writer.indent('def __init__(self, **kwargs)'):
            # initialize variables with default values
            for (variables, comment, is_input) in [
                    (self.parser.input_vars, 'input variables', True),
                    (self.parser.output_vars, 'output variables', False),
                    (self.parser.internal_vars, 'internal variables', False),
                ]:
                self.writer.writeln('# ' + comment)
                for var in variables:
                    if var.comment is not None:
                        self.writer.nl()
                        self._write_comment(var.comment, True)
                    self.writer.writeln('self.{name} = {value}'.format(
                        name=var.name,
                        value=self.convert_to_python(var.default)
                    ))
                    if is_input:
                        with self.writer.indent('if "{}" in kwargs'.format(var.name)):
                            self.writer.writeln('self.set{cap}(kwargs["{name}"])'.format(
                                cap=var.name.capitalize(),
                                name=var.name
                            ))
                self.writer.nl()

    def _write_method(self, method):
        self.writer.nl()
        with self.writer.indent('def {}(self)'.format(method.name)):
            if method.comment:
                self._write_comment(method.comment, False)
            self._write_stmt_body(method)

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writer.writeln('"""')
        prefix = '# ' if simple else ''
        for line in lines:
            self.writer.writeln(u'{}{}'.format(prefix, line.strip()))
        if not simple:
            self.writer.writeln('"""')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writer.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writer.writeln('self.{}()'.format(part.method_name))
            elif isinstance(part, IfStmt):
                self._write_if(part)
            elif isinstance(part, ElseStmt):
                self._write_else(part)
            elif isinstance(part, ThenStmt):
                # avoid empty if-statement body
                if part and part.body:
                    self._write_stmt_body(part)
                else:
                    self.writer.writeln('pass')

    def _write_if(self, stmt):
        converted = self._convert_if(stmt.condition)
        with self.writer.indent('if {}'.format(converted)):
            self._write_stmt_body(stmt)

    def _write_else(self, stmt):
        if not stmt.body:
            # avoid empty else stmts
            return
        self.writer.dec_indent()
        self.writer.writeln('else:')
        self.writer.inc_indent()
        self._write_stmt_body(stmt)

    def _convert_exec(self, expr):
        expr = remove_size_literal(expr)
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['self.', var, ' = ']
        ret += self.to_code(parsed_stmt)
        return ''.join(ret)

    def _convert_if(self, expr):
        expr = remove_size_literal(expr)
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(self.to_code(compare_stmt))

    def convert_to_python(self, value):
        """ Convert a java-like expression to valid python code """
        value = remove_size_literal(value)
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.to_code(node))
