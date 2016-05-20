"""
PHP writer
BigDecimal functionality is provided by Brick/Math PHP module,
see https://github.com/brick/math
"""
import ast
from .. import (
    prepare_expr,
    parse_eval_stmt,
    parse_condition_stmt,
    remove_size_literal
)
from .base import Writer
from .. import (
    EvalStmt,
    IfStmt,
    ThenStmt,
    ElseStmt,
    ExecuteStmt,
)

class PhpWriter(Writer):
    """ PHP Writer """

    bd_static_map = {
        'ZERO': 'zero()',
        'ONE': 'one()',
        'TEN': 'ten()',
        'valueOf': 'of'
    }

    bd_aliases_map = {
        'multiply': 'multipliedBy',
        'divide': 'dividedBy',
        'add': 'plus',
        'subtract': 'minus',
        'setScale': 'withScale',
    }

    def __init__(self, parser, outfile, class_name=None, ns_name='', indent='    '):
        super(PhpWriter, self).__init__(outfile, indent)
        self.parser = parser
        self.class_name = class_name
        self.ns_name = ns_name

    def _write_preamble(self):
        self.writeln('<?php')
        self.nl()
        if self.ns_name:
            self.writeln("namespace {};".format(self.ns_name))
            self.nl()
        self.writeln(r"include('vendor/autoload.php');")
        self.writeln(r"use Brick\Math\BigDecimal as BigDecimal;")
        self.writeln(r"use Brick\Math\RoundingMode as RoundingMode;")
        self.nl()

    def generate(self):
        """ Generates PHP code """
        class_name = self.class_name if self.class_name else self.parser.internal_name
        self._write_preamble()
        self.writeln('class {} {{'.format(class_name))
        with self.indent():
            self._write_comment('Internal variables', False)
            for var in self.parser.internal_vars:
                self._write_var(var)
            self.nl()
            self._write_comment('Input variables', False)
            for var in self.parser.input_vars:
                self._write_var(var)
            self.nl()
            self._write_comment('Output variables', False)
            for var in self.parser.output_vars:
                self._write_var(var)
            self._write_constructor()
            self._write_initializer()
            # create getters for output vars
            for var in self.parser.output_vars:
                self.nl()
                self.writeln('public function get{}() {{'.format(var.name.capitalize()))
                with self.indent():
                    self.writeln('return $this->{};'.format(var.name))
                self.writeln('}')

            # create setters for input vars
            for var in self.parser.input_vars:
                self.nl()
                self.writeln('public function set{}($value) {{'.format(var.name.capitalize()))
                with self.indent():
                    if var.type == 'BigDecimal':
                        self.writeln('$this->{} = BigDecimal::of($value);'.format(var.name))
                    else:
                        self.writeln('$this->{} = $value;'.format(var.name))
                self.writeln('}')

            self._write_method(self.parser.main_method, 'public')
            for method in self.parser.methods:
                self._write_method(method)
        self.writeln('}')

    def _write_constructor(self):
        self.nl()
        self.writeln('public function __construct() {')
        with self.indent():
            self.writeln('$this->initialize();')
        self.writeln('}')

    def _write_initializer(self):
        self.nl()
        self.writeln('protected function initialize() {')
        with self.indent():
            # initialize variables with default values and set "constants"
            for (variables, comment) in [
                    (self.parser.internal_vars, 'Initialize internal variables'),
                    (self.parser.input_vars, 'Initialize input variables'),
                    (self.parser.output_vars, 'Initialize output variables')
                ]:
                self.writeln('// ' + comment)
                for var in variables:
                    default = var.default
                    if not default:
                        if var.type == 'BigDecimal':
                            default = 'BigDecimal.valueOf(0)'
                        else:
                            default = '0'
                    self.writeln('$this->{name} = {value};'.format(
                        name=var.name,
                        value=convert_to_php(default)
                    ))
                self.nl()
            self.writeln('// Initialize "constants"')
            for const in self.parser.constants:
                value = const.value
                if const.type.endswith('[]'):
                    value = '[{}]'.format(value[1:-1])
                converted = convert_to_php(value)
                self.writeln('$this->{const.name} = {converted};'.format(
                    const=const, converted=converted
                ))
        self.writeln('}')

    def _write_var(self, var):
        if var.comment is not None:
            self.nl()
            self._write_comment(var.comment, True)
        self.writeln('private ${};'.format(var.name))

    def _write_method(self, method, visibility='protected'):
        self.nl()
        if method.comment:
            self._write_comment(method.comment, False)
        self.writeln('{visibility} function {method.name}() {{'.format(
            visibility=visibility,
            method=method
        ))
        # actual method body
        with self.indent():
            self._write_stmt_body(method)
        # end method body
        self.writeln('}')

    def _write_comment(self, comment, simple=True):
        lines = comment.split("\n")
        if not simple:
            self.writeln('/**')
        prefix = '//' if simple else ' *'
        for line in lines:
            self.writeln('{} {}'.format(prefix, line.strip()))
        if not simple:
            self.writeln(' */')

    def _write_stmt_body(self, stmt):
        for part in stmt.body:
            if isinstance(part, EvalStmt):
                self.writeln(self._convert_exec(part.expr))
            elif isinstance(part, ExecuteStmt):
                self.writeln('$this->{}();'.format(part.method_name))
            elif isinstance(part, IfStmt):
                self._write_if(part)
            elif isinstance(part, ElseStmt):
                self._write_else(part)
            elif isinstance(part, ThenStmt):
                self._write_stmt_body(part)

    def _write_if(self, stmt):
        converted = self._convert_if(stmt.condition)
        self.writeln('if ({}) {{'.format(converted))
        with self.indent():
            self._write_stmt_body(stmt)
        self.writeln('}')

    def _write_else(self, stmt):
        if not stmt.body:
            # avoid empty else stmts
            return
        self.dec_indent()
        self.writeln('} else {')
        self.inc_indent()
        self._write_stmt_body(stmt)

    def _convert_exec(self, expr):
        expr = remove_size_literal(expr)
        (var, parsed_stmt) = parse_eval_stmt(expr)
        ret = ['$this->', var, ' = ']
        ret += astnode_to_php(parsed_stmt)
        ret.append(";")
        return ''.join(ret)

    def _convert_if(self, expr):
        expr = remove_size_literal(expr)
        compare_stmt = parse_condition_stmt(expr)
        return ''.join(astnode_to_php(compare_stmt))

def convert_to_php(value):
    value = remove_size_literal(value)
    tree = ast.parse(prepare_expr(value))
    node = tree.body[0].value
    return ''.join(astnode_to_php(node))

def astnode_to_php(node):
    """ convert an AST node to its PHP representation """
    if isinstance(node, ast.Attribute):
        ret = astnode_to_php(node.value) + ['->', node.attr]
        if ret[-3] == 'BigDecimal':
            if node.attr in PhpWriter.bd_static_map:
                ret[-2] = '::'
                ret[-1] = PhpWriter.bd_static_map[node.attr]
                return ret
            if node.attr.startswith('ROUND_'):
                return ret[:-3] + ['RoundingMode::' + node.attr[6:]]
        return ret
    if isinstance(node, ast.BinOp):
        return (
            astnode_to_php(node.left) +
            astnode_to_php(node.op) +
            astnode_to_php(node.right)
        )
    if isinstance(node, ast.Name):
        if node.id == 'BigDecimal':
            return [node.id]
        elif node.id == 'BigDecimalConstructor':
            return ['BigDecimal', '::', 'of']
        return ['$this->{}'.format(node.id)]
    if isinstance(node, ast.Add):
        return [' + ']
    if isinstance(node, ast.Sub):
        return [' - ']
    if isinstance(node, ast.Num):
        return [str(node.n)]
    if isinstance(node, ast.BoolOp):
        vals = []
        op = ' && '
        if isinstance(node.op, ast.Or):
            op = ' || '
        for (idx, val) in enumerate(node.values):
            vals += astnode_to_php(val)
            if idx != len(node.values) - 1:
                vals.append(op)
        return vals
    if isinstance(node, ast.UnaryOp):
        op = '-'
        if isinstance(node.op, ast.UAdd):
            op = '+'
        return [op] + astnode_to_php(node.operand)
    if isinstance(node, ast.Subscript):
        return (
            astnode_to_php(node.value) +
            ['['] +
            astnode_to_php(node.slice.value) +
            [']']
        )
    if isinstance(node, ast.Call):
        args = []
        caller = astnode_to_php(node.func)
        if caller[-1] in PhpWriter.bd_aliases_map:
            caller[-1] = PhpWriter.bd_aliases_map[caller[-1]]
        if len(node.args) == 1 and caller[-1] == 'dividedBy':
            caller[-1] = 'exactlyDividedBy'
        for (idx, arg) in enumerate(node.args):
            args += astnode_to_php(arg)
            if idx != len(node.args) - 1:
                args.append(', ')
        return caller + ['('] + args + [')']
    if isinstance(node, ast.List):
        ret = ['array(']
        for (idx, elt) in enumerate(node.elts):
            ret += astnode_to_php(elt)
            if idx != len(node.elts) - 1:
                ret.append(', ')
        ret.append(')')
        return ret
    if isinstance(node, ast.Compare):
        return (
            astnode_to_php(node.left) +
            astnode_to_php(node.ops[0]) +
            astnode_to_php(node.comparators[0])
        )
    if isinstance(node, ast.Lt):
        return [' < ']
    if isinstance(node, ast.LtE):
        return [' =< ']
    if isinstance(node, ast.Eq):
        return [' === ']
    if isinstance(node, ast.Gt):
        return [' > ']
    if isinstance(node, ast.GtE):
        return [' >= ']
    if isinstance(node, ast.NotEq):
        return [' != ']
    if isinstance(node, ast.Mult):
        return [' * ']
    if isinstance(node, ast.Div):
        return [' / ']
    raise ValueError("Unknown AST element: {}".format(node))
