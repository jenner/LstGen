# coding: utf-8
"""
AST to code converter base class
"""
import ast


class AstToCode(object):
    """ converts an AST to code """

    property_accessor_op = '.'
    """ Default property accessor operator for OOP """

    constant_accessor_op = '.'
    """ Default constant accessor operator for OOP """

    instance_var = 'self'
    """ Name of the implicit instance variable (if any) """

    add_op = '+'
    """ Addition operator (usually a "+") """

    unary_add_op = '+'
    """ Unary addition operator as in "+x" (usually a "+") """

    sub_op = '-'
    """ Subtraction operator (usually a "-") """

    unary_sub_op = '-'
    """ Unary subtraction operator as in "-x" (usually a "-") """

    mult_op = '*'
    """ Multiplication operator (usually a "*") """

    div_op = '/'
    """ Division operator (usually a "/") """

    list_subscription_parens = ('[', ']')
    """ Parenthesis to access a list/array member (subscription) """

    callable_exec_parens = ('(', ')')
    """ Parenthesis that denote the execution of a callable, as in "foo()" """

    call_args_delim = ', '
    """ Delimiter for function/method/callable arguments, usually a ", " """

    list_members_delim = ', '
    """ Delimiter for list/array members, usually a ", " """

    list_const_parens = ('[', ']')
    """ List/array constructor parenthesis, usually [], note that in case of PHP it's array() """

    bool_and = '&&'
    """ Boolean AND operator """

    bool_or = '||'
    """ Boolean OR operator """

    cmp_lt_op = '<'
    cmp_lte_op = '<='
    cmp_gt_op = '>'
    cmp_gte_op = '>='
    cmp_eq_op = '=='
    cmp_neq_op = '!='
    """ Comparison operators """

    bd_class = 'BigDecimal'
    """ BigDecimal class or its alias """

    bd_class_constructor = 'new BigDecimal'
    """ BigDecimal constructor statement, as in "new BigDecimal()" """

    allow_constants = True
    """ Allow usage of class constants (orf final static fields) """

    def __init__(self, parser, class_name=None):
        self.parser = parser
        self.class_name = class_name if class_name else self.parser.internal_name

    @property
    def inst_prefix(self):
        return '{}{}'.format(
            self.instance_var,
            self.property_accessor_op
        ) if self.instance_var else ''


    def _conv_attribute(self, node):
        return (
            self.to_code(node.value) +
            [self.property_accessor_op, node.attr]
        )

    def _conv_binop(self, node):
        return (
            self.to_code(node.left) +
            self.to_code(node.op) +
            self.to_code(node.right)
        )

    def _conv_name(self, node):
        if node.id == 'BigDecimal':
            return [self.bd_class]
        elif node.id == 'BigDecimalConstructor':
            return [self.bd_class_constructor]
        if self.allow_constants and node.id in self.parser.constant_names:
            return ['{}{}{}'.format(
                self.class_name,
                self.constant_accessor_op,
                node.id
            )]
        return ['{}{}'.format(self.inst_prefix, node.id)]

    def _conv_number(self, node):
        return [str(node.n)]

    def _conv_bool_op(self, node):
        vals = []
        op = self.bool_and
        if isinstance(node.op, ast.Or):
            op = self.bool_or
        op = ' {} '.format(op)
        for (idx, val) in enumerate(node.values):
            vals += self.to_code(val)
            if idx != len(node.values) - 1:
                vals.append(op)
        return vals

    def _conv_unary_op(self, node):
        op = self.unary_sub_op if isinstance(node.op, ast.USub) else self.unary_add_op
        return [op] + self.to_code(node.operand)

    def _conv_list_subscript(self, node):
        return (
            self.to_code(node.value) +
            [self.list_subscription_parens[0]] +
            self.to_code(node.slice.value) +
            [self.list_subscription_parens[1]]
        )

    def _conv_call(self, node):
        args = []
        caller = self.to_code(node.func)
        for (idx, arg) in enumerate(node.args):
            args += self.to_code(arg)
            if idx != len(node.args) - 1:
                args.append(self.call_args_delim)
        return (
            caller +
            [self.callable_exec_parens[0]] +
            args +
            [self.callable_exec_parens[1]]
        )

    def _conv_comp(self, node):
        return (
            self.to_code(node.left) +
            self.to_code(node.ops[0]) +
            self.to_code(node.comparators[0])
        )

    def _conv_list(self, node):
        ret = [self.list_const_parens[0]]
        for (idx, elt) in enumerate(node.elts):
            ret += self.to_code(elt)
            if idx != len(node.elts) - 1:
                ret.append(self.list_members_delim)
        ret.append(self.list_const_parens[1])
        return ret

    def _conv_cmp_lt(self, node):
        return [' {} '.format(self.cmp_lt_op)]

    def _conv_cmp_lte(self, node):
        return [' {} '.format(self.cmp_lte_op)]

    def _conv_cmp_eq(self, node):
        return [' {} '.format(self.cmp_eq_op)]

    def _conv_cmp_gt(self, node):
        return [' {} '.format(self.cmp_gt_op)]

    def _conv_cmp_gte(self, node):
        return [' {} '.format(self.cmp_gte_op)]

    def _conv_cmp_neq(self, node):
        return [' {} '.format(self.cmp_neq_op)]

    def _conv_add_op(self, node):
        return [' {} '.format(self.add_op)]

    def _conv_sub_op(self, node):
        return [' {} '.format(self.sub_op)]

    def _conv_mult_op(self, node):
        return [' {} '.format(self.mult_op)]

    def _conv_div_op(self, node):
        return [' {} '.format(self.div_op)]

    def to_code(self, node):
        """ convert an AST node to its specific language representation """
        if isinstance(node, ast.Attribute):
            return self._conv_attribute(node)

        if isinstance(node, ast.BinOp):
            return self._conv_binop(node)

        if isinstance(node, ast.Name):
            return self._conv_name(node)

        if isinstance(node, ast.Num):
            return self._conv_number(node)

        if isinstance(node, ast.BoolOp):
            return self._conv_bool_op(node)

        if isinstance(node, ast.UnaryOp):
            return self._conv_unary_op(node)

        if isinstance(node, ast.Subscript):
            return self._conv_list_subscript(node)

        if isinstance(node, ast.Call):
            return self._conv_call(node)

        if isinstance(node, ast.List):
            return self._conv_list(node)

        if isinstance(node, ast.Compare):
            return self._conv_comp(node)

        if isinstance(node, ast.Lt):
            return self._conv_cmp_lt(node)

        if isinstance(node, ast.LtE):
            return self._conv_cmp_lte(node)

        if isinstance(node, ast.Eq):
            return self._conv_cmp_eq(node)

        if isinstance(node, ast.Gt):
            return self._conv_cmp_gt(node)

        if isinstance(node, ast.GtE):
            return self._conv_cmp_gte(node)

        if isinstance(node, ast.NotEq):
            return self._conv_cmp_neq(node)

        if isinstance(node, ast.Add):
            return self._conv_add_op(node)

        if isinstance(node, ast.Sub):
            return self._conv_sub_op(node)

        if isinstance(node, ast.Mult):
            return self._conv_mult_op(node)

        if isinstance(node, ast.Div):
            return self._conv_div_op(node)

        raise ValueError(u'Unknown AST element: {}'.format(node))
