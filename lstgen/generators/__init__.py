# coding: utf-8
"""
Base code generators module
"""
from .php import PhpGenerator
from .python import PythonGenerator
from .java import JavaGenerator

__all__ = ['PhpGenerator', 'PythonGenerator', 'JavaGenerator']

GENERATORS = {
    'php': PhpGenerator,
    'python': PythonGenerator,
    'java': JavaGenerator
}
