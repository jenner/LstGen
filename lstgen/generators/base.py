# coding: utf-8
"""
Base writers module
"""
from contextlib import contextmanager

from .ast2code import AstToCode

from .. import (
    parse_eval_stmt,
    parse_condition_stmt
)
from .. import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)


class Writer(object):
    """ Basic writer class used to write structured
        code with indentation to a file-like object.
    """

    default_indent_str = ' ' * 4
    """ Default indentation string (4 spaces)"""

    def __init__(self, outfile, indent_str=None, block_chars=(' {', '}')):
        self.outfile = outfile
        self.block_chars = block_chars
        self.indent_str = indent_str if indent_str is not None else self.default_indent_str
        self.indent_lvl = 0

    def generate(self):
        raise Exception("Implement me!")

    def write(self, content, do_indent=True):
        """ Write content to outfile with optional indentation """
        if not content:
            return
        if do_indent:
            self.outfile.write(self.indent_str * self.indent_lvl)
        self.outfile.write(content)

    def writeln(self, content, do_indent=True):
        """ Write content to outfile finishing with a new-line """
        self.write(content, do_indent)
        self.nl()

    def nl(self, num=1, do_indent=False):
        """ Write a new-line to outfile """
        self.write("\n" * num, do_indent)

    def inc_indent(self, lvl=1):
        """ Increase indentation level """
        self.indent_lvl += lvl

    def dec_indent(self, lvl=1):
        """ Decrease indentation level """
        if self.indent_lvl > 0:
            self.indent_lvl -= lvl

    @contextmanager
    def indent(self, preamble, lvl=1):
        """ Allows creating visual indented blocks
            that produce actual code blocks:

            with x.indent('def foo()'):
                x.writeln('print("Hello World!"))
                x.writeln('return 1')
        """
        self.writeln('{}{}'.format(preamble, self.block_chars[0]))
        self.inc_indent(lvl)
        yield
        self.dec_indent(lvl)
        if self.block_chars[1]:
            self.writeln(self.block_chars[1])


class BaseGenerator(AstToCode):
    """ Base code generator class """

    def __init__(self, parser, outfile, class_name=None, indent=None, block_chars=(' {', '}')):
        super(BaseGenerator, self).__init__(parser, class_name)
        self.writer = Writer(outfile, indent, block_chars)

    def generate(self):
        raise NotImplementedError("Implement me!")


class JavaLikeGenerator(BaseGenerator):
    """ Base generator for java-like code syntax """

    stmt_separator = ';'
    """ Line endings (usually a ";" or empty) """

    instance_var = 'this'
    """ Name of the implicit instance variable (if any) """

    def __init__(self, parser, outfile, class_name=None, indent=None, package_name='default'):
        super(JavaLikeGenerator, self).__init__(parser, outfile, class_name, indent)
        self.package_name = package_name

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
                self.writer.writeln('{}.{}(){}'.format(
                    self.instance_var,
                    part.method_name,
                    self.stmt_separator
                ))
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
        ret = [self.instance_var, '.', var, ' = ']
        ret += self.to_code(parsed_stmt)
        ret.append(self.stmt_separator)
        return ''.join(ret)

    def _convert_if(self, expr):
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(self.to_code(compare_stmt))
