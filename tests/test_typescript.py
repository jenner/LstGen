# coding: utf-8
import os
import unittest
from io import StringIO

from lxml import etree

from lstgen import PapParser
from lstgen.cli import LANGUAGES
from lstgen.generators import GENERATORS, TypescriptGenerator


HERE = __file__


class TestTypescript(unittest.TestCase):

    def setUp(self):
        path = os.path.join(
            os.path.dirname(HERE),
            'data/example_typescript_pap.xml'
        )
        with open(path, encoding='utf-8') as pap_file:
            pap_xml = pap_file.read()
        self.parser = PapParser(etree.fromstring(pap_xml))
        self.out = StringIO()
        self.generator = TypescriptGenerator(
            self.parser,
            self.out,
            class_name='Lohnsteuer2100'
        )

    def test_generate_typed_es_module(self):
        self.generator.generate()
        val = self.out.getvalue()

        assert (
            'import { Big, RoundingMode, type BigDecimal } from "bigdecimal.js";'
            in val
        )
        assert 'export interface Lohnsteuer2100Params {' in val
        assert 'INBAR?: BigDecimal | string;' in val
        assert 'INDOUBLE?: number;' in val
        assert 'export class Lohnsteuer2100 {' in val
        assert 'public constructor(params: Lohnsteuer2100Params = {}) {' in val

        assert 'protected static readonly CONSTFOO: BigDecimal = Big(1);' in val
        assert (
            'protected static readonly CONSTARRAY: ReadonlyArray<BigDecimal> = '
            '[Big(0), Big(2)];' in val
        )
        assert 'protected INFOO: number = 1;' in val
        assert 'protected INBAR: BigDecimal = Big(0);' in val

        assert 'public setInbar(value: BigDecimal | string): void {' in val
        assert 'typeof value === "string" ? Big(value) : value' in val
        assert 'public getOutfoo(): BigDecimal {' in val
        assert 'public MAIN(): void {' in val
        assert 'protected MFOO(): void {' in val
        assert 'RoundingMode.UP' in val

    def test_convert_pap_expressions(self):
        assert self.generator.convert_to_typescript(
            'BigDecimal.valueOf(2)'
        ) == 'Big(2)'
        assert self.generator.convert_to_typescript(
            'new BigDecimal("2.5")'
        ) == 'Big("2.5")'
        assert self.generator.convert_to_typescript(
            'BigDecimal.TEN'
        ) == 'Big(10)'
        assert self.generator.convert_to_typescript(
            'INBAR.longValue()'
        ) == 'Number(this.INBAR.toBigInt())'
        assert self.generator.convert_to_typescript(
            'INBAR.doubleValue()'
        ) == 'this.INBAR.numberValue()'
        assert self.generator._convert_if('INFOO == 1') == 'this.INFOO === 1'
        assert self.generator._convert_exec('INFOO = 10L') == 'this.INFOO = 10;'

    def test_registered_as_cli_language(self):
        assert GENERATORS['typescript'] is TypescriptGenerator
        assert 'typescript' in LANGUAGES


if __name__ == '__main__':
    unittest.main()
