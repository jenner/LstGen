import re
import ast
from lxml import etree

# matches java-like long or double numbers, e.g.
# 123L or 3.12354D
NUMS_WITH_SIZE_RE = re.compile(r'([0-9]+)([LD]{1})')

def remove_size_literal(source):
    """ Remove LONG or DOUBLE literals from number code """
    if NUMS_WITH_SIZE_RE.findall(source):
        return NUMS_WITH_SIZE_RE.sub(r'\1', source)
    return source

def prepare_expr(source):
    replacements = {
        'new BigDecimal': 'BigDecimalConstructor',
        '&&': 'and',
        '||': 'or'
    }
    for (key, repl) in replacements.items():
        source = source.replace(key, repl)
    # watch out for LONG literals

    return source.strip()

def parse_eval_stmt(source):
    """ parse java-like code in exec attribute
        of an EVAL tag
    """
    # remove java-specific constructor calls
    source = prepare_expr(source)
    tree = ast.parse(source)
    # an EVAL always contains a single assingment
    assign = tree.body[0]
    identifier = assign.targets[0].id
    return (identifier, assign.value)


def parse_condition_stmt(source):
    """ parse java-like code in expr attribute
        of an IF tag
    """
    # remove java-specific boolean operators
    source = prepare_expr(source)
    tree = ast.parse(source)
    return tree.body[0].value


def prev_comment(element):
    comment_elm = element.getprevious()
    comment = None
    if comment_elm is not None and comment_elm.tag is etree.Comment:
        comment = comment_elm.text
    return comment

class Comment:

    def __init__(self, content):
        self.content = content

    @classmethod
    def from_element(cls, element):
        return cls(element.text)


class SimpleStmt:

    def __init__(self, comment=None):
        self.comment = comment

    @classmethod
    def from_element(cls, element):
        return cls(prev_comment(element))

class StmtWithBody(SimpleStmt):

    def __init__(self, comment=None):
        super(StmtWithBody, self).__init__(comment)
        self.body = []

    def add(self, stmt):
        self.body.append(stmt)

    @classmethod
    def from_element(cls, element):
        stmt = super(StmtWithBody, cls).from_element(element)
        for child in element.getchildren():
            if child.tag in STMT_MAP:
                stmt.add(STMT_MAP[child.tag].from_element(child))
        return stmt

class EvalStmt(SimpleStmt):

    def __init__(self, comment=None, expr=None):
        super(EvalStmt, self).__init__(comment)
        self.expr = expr

    @classmethod
    def from_element(cls, element):
        stmt = super(EvalStmt, cls).from_element(element)
        stmt.expr = element.get('exec')
        return stmt


class ExecuteStmt(SimpleStmt):

    def __init__(self, comment=None, method_name=None):
        super(ExecuteStmt, self).__init__(comment)
        self.method_name = method_name

    @classmethod
    def from_element(cls, element):
        stmt = super(ExecuteStmt, cls).from_element(element)
        stmt.method_name = element.get('method')
        return stmt


class ThenStmt(StmtWithBody):
    pass

class ElseStmt(StmtWithBody):
    pass

class IfStmt(StmtWithBody):

    def __init__(self, comment=None, condition=None):
        super(IfStmt, self).__init__(comment)
        self.condition = condition

    @classmethod
    def from_element(cls, element):
        stmt = super(IfStmt, cls).from_element(element)
        stmt.condition = element.get('expr')
        return stmt


class Method(StmtWithBody):

    def __init__(self, comment=None, name=None):
        super(Method, self).__init__(comment)
        self.name = name

    @classmethod
    def from_element(cls, element):
        method = super(Method, cls).from_element(element)
        method.name = element.get('name')
        return method


class Prop:

    def __init__(self, name, type):
        self.name = name
        self.type = type


class Var(Prop):

    def __init__(self, name, type, default=None, comment=None):
        super(Var, self).__init__(name, type)
        self.default = default
        self.comment = comment
        if not self.default:
            if self.type == 'int':
                self.default = '0'
            elif self.type == 'BigDecimal':
                self.default = 'new BigDecimal(0)'
        else:
            if self.type == 'int' and '.' in self.default:
                self.default = str(int(float(self.default)))

    @classmethod
    def from_element(cls, element):
        comment = prev_comment(element)
        return cls(
            element.get('name'),
            element.get('type'),
            element.get('default'),
            comment
        )

class Const(Prop):

    def __init__(self, name, type, value, comment=None):
        super(Const, self).__init__(name, type)
        self.value = value
        self.comment = comment

    @classmethod
    def from_element(cls, element):
        comment = prev_comment(element)
        return cls(
            element.get('name'),
            element.get('type'),
            element.get('value'),
            comment
        )


STMT_MAP = {
    'METHOD': Method,
    'IF': IfStmt,
    'THEN': ThenStmt,
    'ELSE': ElseStmt,
    'EVAL': EvalStmt,
    'COMMENT': Comment,
    'EXECUTE': ExecuteStmt,
    'MAIN': Method,
}

class PapParser:

    def __init__(self, tree):
        self.tree = tree
        self.internal_name = None
        self._input_vars = None
        self._output_vars = None
        self._internal_vars = None
        self._constants = None
        self._methods = None
        self.main_method = None

    def parse(self):
        self.repair_tree()
        self.internal_name = self.tree.getroot().get('name')
        main_element = self.tree.xpath('/PAP/METHODS/MAIN')[0]
        main_element.set('name', 'MAIN')
        self.main_method = Method.from_element(main_element)

    def repair_tree(self):
        """ Move <else></else> element outside of an <if></if> element
            back into <if> parent, see e.g. method MZTABFB from Lohnsteuer2010.xml
        """
        for elm in self.tree.xpath('//IF'):
            else_elm = elm.getnext()
            if else_elm is not None and else_elm.tag == 'ELSE':
                elm.getparent().remove(else_elm)
                elm.append(else_elm)

    @property
    def methods(self):
        if not self._methods:
            self._methods = []
            for method in self.tree.xpath('/PAP/METHODS/METHOD'):
                self._methods.append(Method.from_element(method))
        return self._methods

    def _get_vars(self, xpath):
        for var in self.tree.xpath(xpath):
            yield Var.from_element(var)

    @property
    def input_vars(self):
        if not self._input_vars:
            self._input_vars = list(self._get_vars('/PAP/VARIABLES/INPUTS/INPUT'))
        return self._input_vars

    @property
    def output_vars(self):
        if not self._output_vars:
            self._output_vars = list(self._get_vars('/PAP/VARIABLES/OUTPUTS/OUTPUT'))
        return self._output_vars

    @property
    def internal_vars(self):
        if not self._internal_vars:
            self._internal_vars = list(self._get_vars('/PAP/VARIABLES/INTERNALS/INTERNAL'))
        return self._internal_vars

    @property
    def constants(self):
        if not self._constants:
            self._constants = [
                Const.from_element(const)
                for const in self.tree.xpath('/PAP/CONSTANTS/CONSTANT')
            ]
        return self._constants
