# coding: utf-8
"""
Base writers module
"""
from contextlib import contextmanager
from abc import ABCMeta, abstractmethod

class Writer(metaclass=ABCMeta):
    """ Basic writer class used to write structured
        code with indentation to a file-like object.
    """

    default_indent_str = ' ' * 4
    """ Default indentation string (4 spaces)"""

    def __init__(self, outfile, indent_str=None):
        self.outfile = outfile
        self.indent_str = indent_str if indent_str is not None else self.default_indent_str
        self.indent_lvl = 0

    @abstractmethod
    def generate(self):
        pass

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
        for i in range(num):
            self.write("\n", do_indent)

    def inc_indent(self, lvl=1):
        """ Increase indentation level """
        self.indent_lvl += lvl

    def dec_indent(self, lvl=1):
        """ Decrease indentation level """
        if self.indent_lvl > 0:
            self.indent_lvl -= lvl

    @contextmanager
    def indent(self, lvl=1):
        """ Allows creating visual indented blocks
            that produce actual code blocks:

            x.writeln('def foo():')
            with x.indent():
                x.writeln('print("Hello World!"))
                x.writeln('return 1')
        """
        self.inc_indent(lvl)
        yield
        self.dec_indent(lvl)
