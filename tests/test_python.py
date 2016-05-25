# coding: utf-8
import unittest
import os
from lxml import etree
from io import StringIO
from six import u
from lstgen import PapParser
from lstgen.writers.python import PythonWriter


HERE = __file__


class TestPython(unittest.TestCase):

    def setUp(self):
        path = os.path.join(os.path.dirname(HERE), 'data/example_pap.xml')
        pap_xml = open(path).read()
        self.parser = PapParser(etree.fromstring(pap_xml))
        self.out = StringIO()
        self.writer = PythonWriter(
            self.parser,
            self.out,
            class_name="üäö"
        )

    def test_generate(self):
        self.writer.generate()
        val = self.out.getvalue()
        assert u('class BigDecimal(decimal.Decimal):') in val
        assert u('def __init__(self, **kwargs):') in val

        assert u('def setInfoo(self, value):') in val
        assert u('def setInbar(self, value):') in val
        assert u('def setInblah(self, value):') in val

        assert u('def getOutfoo(self):') in val
        assert u('def getOutbar(self):') in val
        assert u('def getOutblah(self):') in val

        assert u('def MFOO(self):') in val
        assert u('def MBAR(self):') in val
