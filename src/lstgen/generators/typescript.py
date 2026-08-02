"""
TypeScript generator
"""
import ast
import json

from .. import prepare_expr, remove_size_literal
from .base import JavaLikeGenerator


class TypescriptGenerator(JavaLikeGenerator):
    """Generate a typed ES module from a PAP definition."""

    bd_class_constructor = 'Big'
    cmp_eq_op = '==='
    cmp_neq_op = '!=='

    type_aliases = {
        'int': 'number',
        'double': 'number',
        'BigDecimal': 'BigDecimal',
    }

    bd_attr_aliases = {
        'ZERO': 'Big(0)',
        'ONE': 'Big(1)',
        'TEN': 'Big(10)',
        'valueOf': 'Big',
        'ROUND_UP': 'RoundingMode.UP',
        'ROUND_DOWN': 'RoundingMode.DOWN',
        'ROUND_CEILING': 'RoundingMode.CEILING',
        'ROUND_FLOOR': 'RoundingMode.FLOOR',
        'ROUND_HALF_UP': 'RoundingMode.HALF_UP',
        'ROUND_HALF_DOWN': 'RoundingMode.HALF_DOWN',
        'ROUND_HALF_EVEN': 'RoundingMode.HALF_EVEN',
        'ROUND_UNNECESSARY': 'RoundingMode.UNNECESSARY',
    }

    @property
    def params_name(self):
        """Name of the generated constructor parameter interface."""
        return '{}Params'.format(self.class_name)

    def generate(self):
        wr = self.writer

        wr.writeln(
            'import { Big, RoundingMode, type BigDecimal } from "bigdecimal.js";'
        )
        wr.nl()

        self._write_params_interface()
        wr.nl()

        with wr.indent('export class {}'.format(self.class_name)):
            self._write_constants()
            self._write_fields()
            self._write_constructor()
            self._write_setters()
            self._write_getters()
            self._write_method(self.parser.main_method, 'public')
            for method in self.parser.methods:
                self._write_method(method, 'protected')

    def _write_params_interface(self):
        wr = self.writer
        with wr.indent('export interface {}'.format(self.params_name)):
            for var in self.parser.input_vars:
                if var.comment is not None:
                    self._write_comment(var.comment, False)
                wr.writeln('{}?: {};'.format(
                    var.name,
                    self._input_type(var.type)
                ))

    def _write_constants(self):
        wr = self.writer
        wr.writeln('/* Constants */')
        for const in self.parser.constants:
            if const.comment is not None:
                wr.nl()
                self._write_comment(const.comment, False)
            value = const.value
            if const.type.endswith('[]'):
                value = '[{}]'.format(value[1:-1])
            wr.writeln(
                'protected static readonly {name}: {type} = {value};'.format(
                    name=const.name,
                    type=self._typescript_type(const.type, readonly=True),
                    value=self.convert_to_typescript(value),
                )
            )

    def _write_fields(self):
        wr = self.writer
        for comment, variables in [
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
                wr.writeln(
                    'protected {name}: {type} = {value};'.format(
                        name=var.name,
                        type=self._typescript_type(var.type),
                        value=self.convert_to_typescript(var.default),
                    )
                )

    def _write_constructor(self):
        wr = self.writer
        wr.nl()
        signature = 'public constructor(params: {} = {{}})'.format(self.params_name)
        with wr.indent(signature):
            for var in self.parser.input_vars:
                with wr.indent('if (params.{0} !== undefined)'.format(var.name)):
                    wr.writeln('this.set{cap}(params.{name});'.format(
                        cap=var.name.capitalize(),
                        name=var.name,
                    ))

    def _write_setters(self):
        wr = self.writer
        for var in self.parser.input_vars:
            wr.nl()
            signature = 'public set{cap}(value: {type}): void'.format(
                cap=var.name.capitalize(),
                type=self._input_type(var.type),
            )
            with wr.indent(signature):
                if var.type == 'BigDecimal':
                    wr.writeln(
                        'this.{0} = typeof value === "string" ? Big(value) : value;'.format(
                            var.name
                        )
                    )
                else:
                    wr.writeln('this.{} = value;'.format(var.name))

    def _write_getters(self):
        wr = self.writer
        for var in self.parser.output_vars:
            wr.nl()
            signature = 'public get{cap}(): {type}'.format(
                cap=var.name.capitalize(),
                type=self._typescript_type(var.type),
            )
            with wr.indent(signature):
                wr.writeln('return this.{};'.format(var.name))

    def _write_method(self, method, visibility):
        self.writer.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        signature = '{visibility} {name}(): void'.format(
            visibility=visibility,
            name=method.name,
        )
        with self.writer.indent(signature):
            self._write_stmt_body(method)

    def _typescript_type(self, pap_type, readonly=False):
        if pap_type.endswith('[]'):
            member_type = self._typescript_type(pap_type[:-2])
            if readonly:
                return 'ReadonlyArray<{}>'.format(member_type)
            return '{}[]'.format(member_type)
        return self.type_aliases.get(pap_type, pap_type)

    def _input_type(self, pap_type):
        converted = self._typescript_type(pap_type)
        if pap_type == 'BigDecimal':
            return '{} | string'.format(converted)
        return converted

    def _conv_attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == 'BigDecimal':
            alias = self.bd_attr_aliases.get(node.attr)
            if alias is not None:
                return [alias]
        return super(TypescriptGenerator, self)._conv_attribute(node)

    def _conv_call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('intValue', 'longValue'):
                return (
                    ['Number('] +
                    self.to_code(node.func.value) +
                    ['.toBigInt())']
                )
            if node.func.attr in ('doubleValue', 'floatValue'):
                return self.to_code(node.func.value) + ['.numberValue()']
        return super(TypescriptGenerator, self)._conv_call(node)

    def _conv_list_subscript(self, node):
        """Assert that PAP-controlled array indices resolve to a value."""
        return (
            super(TypescriptGenerator, self)._conv_list_subscript(node) +
            ['!']
        )

    def _conv_number(self, node):
        if isinstance(node.value, str):
            return [json.dumps(node.value, ensure_ascii=False)]
        if node.value is True:
            return ['true']
        if node.value is False:
            return ['false']
        if node.value is None:
            return ['null']
        return super(TypescriptGenerator, self)._conv_number(node)

    def _convert_exec(self, expr):
        return super(TypescriptGenerator, self)._convert_exec(
            remove_size_literal(expr)
        )

    def _convert_if(self, expr):
        return super(TypescriptGenerator, self)._convert_if(
            remove_size_literal(expr)
        )

    def convert_to_typescript(self, value):
        """Convert a Java-like PAP expression to TypeScript."""
        value = remove_size_literal(value)
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.to_code(node))
