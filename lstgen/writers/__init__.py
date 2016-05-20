from contextlib import contextmanager

class Writer:

    default_indent_str = ' ' * 4

    def __init__(self, outfile, indent_str=None):
        self.outfile = outfile
        self.indent_str = indent_str if indent_str is not None else self.default_indent_str
        self.indent_lvl = 0

    def write(self, content, do_indent=True):
        if not content:
            return
        if do_indent:
            self.outfile.write(self.indent_str * self.indent_lvl)
        self.outfile.write(content)

    def writeln(self, content, do_indent=True):
        self.write(content, do_indent)
        self.nl()

    def nl(self, num=1, do_indent=False):
        for i in range(num):
            self.write("\n", do_indent)

    def inc_indent(self, lvl=1):
        self.indent_lvl += lvl

    def dec_indent(self, lvl=1):
        if self.indent_lvl > 0:
            self.indent_lvl -= lvl

    @contextmanager
    def indent(self, lvl=1):
        self.inc_indent()
        yield
        self.dec_indent()
