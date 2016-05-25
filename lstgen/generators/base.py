# coding: utf-8
"""
Base writers module
"""
from contextlib import contextmanager

from .ast2code import AstToCode


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
        self.writer = Writer(outfile, indent, block_chars)
        self.parser = parser
        self.class_name = class_name if class_name else self.parser.internal_name

    def generate(self):
        raise NotImplementedError("Implement me!")
