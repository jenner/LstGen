"""
Javascript generator
"""
import ast
from .. import (
    prepare_expr,
    remove_size_literal
)
from .base import JavaLikeGenerator

class JavascriptGenerator(JavaLikeGenerator):
    """ Javascript Generator """

    bd_attr_aliases = {
        'ZERO': 'ZERO()',
        'ONE': 'ONE()',
        'TEN': 'TEN()',
    }

    def generate(self):
        wr = self.writer
        with self.writer.indent('function {}(params)'.format(self.class_name)):
            # create input and output vars
            for (comment, variables, is_input) in [
                    ('Input variables', self.parser.input_vars, True),
                    ('Output variables', self.parser.output_vars, False),
                    ('Internal variables', self.parser.internal_vars, False),
                ]:
                wr.nl()
                wr.writeln('/* {} */'.format(comment))
                for var in variables:
                    if var.comment is not None:
                        wr.nl()
                        self._write_comment(var.comment, False)
                    default = 'null'
                    if var.default:
                        val = remove_size_literal(var.default)
                        default = self.convert_to_js(val)
                    wr.writeln('this.{name} = {default};'.format(
                        name=var.name,
                        default=default
                    ))
                    if is_input:
                        with self.writer.indent('if (params["{}"] !== undefined)'.format(var.name)):
                            self.writer.writeln('this.set{cap}(params["{name}"]);'.format(
                                cap=var.name.capitalize(),
                                name=var.name
                            ))

        wr.nl()
        wr.writeln("/* Constants */")
        const_tpl = ("Object.defineProperty({self.class_name}, '{const.name}', "
                     "{{value: {converted}}});")
        for const in self.parser.constants:
            if const.comment is not None:
                wr.nl()
                self._write_comment(const.comment, False)
            value = const.value
            if const.type.endswith('[]'):
                value = '[{}]'.format(value[1:-1])
            converted = self.convert_to_js(value)
            wr.writeln(const_tpl.format(
                self=self,
                const=const,
                converted=converted
            ))
        # create setters for input vars
        var_tpl = '{self.class_name}.prototype.set{cap} = function(value)'
        for var in self.parser.input_vars:
            wr.nl()
            signature = var_tpl.format(
                self=self,
                cap=var.name.capitalize()
            )
            with wr.indent(signature):
                wr.writeln('this.{} = value;'.format(var.name))

        # create getters for output vars
        getter_tpl = '{self.class_name}.prototype.get{cap} = function()'
        for var in self.parser.output_vars:
            wr.nl()
            signature = getter_tpl.format(
                self=self,
                cap=var.name.capitalize(),
            )
            with wr.indent(signature):
                wr.writeln('return this.{};'.format(var.name))
        self._write_method(self.parser.main_method)
        for method in self.parser.methods:
            self._write_method(method)

    def _write_method(self, method):
        self.writer.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        signature = '{self.class_name}.prototype.{name} = function()'.format(
            self=self,
            name=method.name
        )
        # actual method body
        with self.writer.indent(signature):
            self._write_stmt_body(method)

    def _conv_attribute(self, node):
        """ Override BaseGenerator in order to replace
            ZERO, ONE and TEN BigDecimal class constants
        """
        attr = node.attr
        val = self.to_code(node.value)
        accop = self.property_accessor_op
        if attr in self.bd_attr_aliases:
            attr = self.bd_attr_aliases[attr]
            accop = self.constant_accessor_op
        return val + [accop, attr]

    def convert_to_js(self, value):
        """ Converts java pseudo code into valid java code """
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.to_code(node))
