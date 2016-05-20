# coding: utf-8
"""
Base writers module
"""
from .php import PhpWriter
from .python import PythonWriter
from .java import JavaWriter

__all__ = ['PhpWriter', 'PythonWriter', 'JavaWriter']

WRITERS = {
    'php': PhpWriter,
    'python': PythonWriter,
    'java': JavaWriter
}
