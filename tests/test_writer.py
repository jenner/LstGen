# coding: utf-8
import unittest
from lstgen.writers.base import Writer
from io import StringIO
from six import u

class TestWriter(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        self.writer = Writer(self.out)

    def test_write(self):
        content = u("üäö")
        self.writer.write(content)
        assert content == self.out.getvalue()

    def test_writeln(self):
        content = u("üäö")
        self.writer.writeln(content)
        assert content != self.out.getvalue()
        assert u("{}\n").format(content) == self.out.getvalue()

    def test_inc_indent(self):
        self.writer.inc_indent()
        self.writer.write("x")
        assert "{}x".format(self.writer.indent_str) == self.out.getvalue()
        self.writer.inc_indent(2)
        self.writer.write("x")
        assert "{}x{}x".format(self.writer.indent_str,  self.writer.indent_str * 3) == self.out.getvalue()

    def test_dec_indent(self):
        self.writer.inc_indent(2)
        self.writer.dec_indent()
        self.writer.write("x")
        assert "{}x".format(self.writer.indent_str) == self.out.getvalue()

    def test_nl(self):
        self.writer.write("x")
        self.writer.nl()
        self.writer.write("y")
        assert "x\ny" == self.out.getvalue()
