"""
PHP writer
BigDecimal functionality is provided by Brick/Math PHP module,
see https://github.com/brick/math
"""
import ast
import os

from ... import (
    prepare_expr,
    parse_eval_stmt,
    parse_condition_stmt,
    remove_size_literal
)
from ... import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)

from .. base import BaseGenerator

class PhpGenerator(BaseGenerator):
    """ PHP Writer """

    property_accessor_op = '->'
    """ PHP property accessor operator """

    constant_accessor_op = '::'
    """ Default constant accessor operator for OOP """

    instance_var = '$this'
    """ Name of the implicit instance variable """

    list_const_parens = ('array(', ')')
    """ List/array constructor parenthesis, usually [], note that
        in case of PHP it's array()
    """

    allow_constants = False
    """ Disallow class constants, since we cannot have instances
        of BigDecimal as constant values
    """

    bd_attr_aliases = {
        'ZERO': 'zero()',
        'ONE': 'one()',
        'TEN': 'ten()',
    }

    bd_statics = (
        'valueOf',
        'ROUND_UP',
        'ROUND_DOWN',
    )

    def __init__(self, parser, outfile, class_name=None, indent=None, ns_name=''):
        super(PhpGenerator, self).__init__(parser, outfile, class_name, indent)
        self.ns_name = ns_name

    def _write_preamble(self):
        self.writer.writeln('<?php')
        self.writer.nl()
        if self.ns_name:
            self.writer.writeln('namespace {};'.format(self.ns_name))
            self.writer.nl()
        # add BigDecimal proxy class
        bd_php_path = os.path.join(os.path.dirname(__file__), 'BigDecimal.php')
        self.writer.nl()
        with open(bd_php_path) as fp:
            self.writer.writeln(fp.read())
        self.writer.nl()

    def generate(self):
        """ Generates PHP code """
        self._write_preamble()
        with self.writer.indent('class {}'.format(self.class_name)):
            self._write_comment('Internal variables', False)
            for var in self.parser.internal_vars:
                self._write_var(var)
            self.writer.nl()
            self._write_comment('Input variables', False)
            for var in self.parser.input_vars:
                self._write_var(var)
            self.writer.nl()
            self._write_comment('Output variables', False)
            for var in self.parser.output_vars:
                self._write_var(var)
            self._write_constructor()
            self._write_initializer()
            # create getters for output vars
            for var in self.parser.output_vars:
                self.writer.nl()
                signature = 'public function get{}()'.format(var.name.capitalize())
                with self.writer.indent(signature):
                    self.writer.writeln('return $this->{};'.format(var.name))

            # create setters for input vars
            for var in self.parser.input_vars:
                self.writer.nl()
                signature = 'public function set{}($value)'.format(var.name.capitalize())
                with self.writer.indent(signature):
                    if var.type == 'BigDecimal':
                        self.writer.writeln('$this->{} = BigDecimal::valueOf($value);'.format(var.name))
                    else:
                        self.writer.writeln('$this->{} = $value;'.format(var.name))

            self._write_method(self.parser.main_method, 'public')
            for method in self.parser.methods:
                self._write_method(method)

    def _write_constructor(self):
        self.writer.nl()
        with self.writer.indent('public function __construct()'):
            self.writer.writeln('$this->initialize();')

    def _write_initializer(self):
        self.writer.nl()
        with self.writer.indent('protected function initialize()'):
            # initialize variables with default values and set "constants"
            for (variables, comment) in [
                    (self.parser.internal_vars, 'Initialize internal variables'),
                    (self.parser.input_vars, 'Initialize input variables'),
                    (self.parser.output_vars, 'Initialize output variables')
                ]:
                self.writer.writeln('// ' + comment)
                for var in variables:
                    default = var.default
                    if not default:
                        if var.type == 'BigDecimal':
                            default = 'BigDecimal.valueOf(0)'
                        else:
                            default = '0'
                    self.writer.writeln('$this->{name} = {value};'.format(
                        name=var.name,
                        value=self.convert_to_php(default)
                    ))
                self.writer.nl()
            self.writer.writeln('// Initialize "constants"')
            for const in self.parser.constants:
                value = const.value
                if const.type.endswith('[]'):
                    value = '[{}]'.format(value[1:-1])
                converted = self.convert_to_php(value)
                self.writer.writeln('$this->{const.name} = {converted};'.format(
                    const=const, converted=converted
                ))

    def _write_var(self, var):
        if var.comment is not None:
            self.writer.nl()
            self._write_comment(var.comment, True)
        self.writer.writeln('private ${};'.format(var.name))

    def _write_method(self, method, visibility='protected'):
        self.writer.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        signature = '{visibility} function {method.name}()'.format(
            visibility=visibility,
            method=method
        )
        with self.writer.indent(signature):
            self._write_stmt_body(method)

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writer.writeln('/**')
        prefix = '//' if simple else ' *'
        for line in lines:
            self.writer.writeln(u'{} {}'.format(prefix, line.strip()))
        if not simple:
            self.writer.writeln(' */')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writer.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writer.writeln('$this->{}();'.format(part.method_name))
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
        expr = remove_size_literal(expr)
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['$this->', var, ' = ']
        ret += self.to_code(parsed_stmt)
        ret.append(";")
        return ''.join(ret)

    def _convert_if(self, expr):
        expr = remove_size_literal(expr)
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(self.to_code(compare_stmt))

    def convert_to_php(self, value):
        value = remove_size_literal(value)
        tree = ast.parse(prepare_expr(value))
        node = tree.body[0].value
        return ''.join(self.to_code(node))

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
        elif attr in self.bd_statics and val[-1] == 'BigDecimal':
            accop = self.constant_accessor_op
        return val + [accop, attr]

