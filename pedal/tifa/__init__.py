"""
Python Type Inferencer and Flow Analyzer (TIFA)

TIFA uses a number of simplifications of the Python language.
  * Variables cannot change type
  * Variables cannot be deleted
  * Complex types have to be homogenous
  * No introspection or reflective characteristics
  * No dunder methods
  * No closures (maybe?)
  * You cannot write a variable out of scope
  * You cannot read a mutable variable out of scope
  * No multiple inheritance

Additionally, it reads the following as issues:
  * Cannot read a variable without having first written to it.
  * Cannot rewrite a variable unless it has been read.

Important concepts:

.. glossary::

    Issue
        A problematic situation in the submitted code that will be reported
        but may not stop the execution. However, when an Issue occurs,
        any results may be invalid.

    Error
        A situation in execution that terminates the program.

    Name
        A name of a variable

    Scope
        The context of a function, with its own namespaces. Represented
        internally using numeric IDs (Scope IDs).

    Scope Chain
        A stack of scopes, with the innermost scope on top.

    Fully Qualified Name
        A string representation of a variable and its scope
        chain, written using "/". For example: 0/1/4/my_variable_name

    Path
        A single path of execution through the control flow; every program
        has at least one sequential path, but IFs, FORs, WHILEs, etc. can
        cause multiple paths. Paths are represented using numeric IDs (Path
        IDs).

    State
        Information about a Name that indicates things like the variable's
        current type and whether that name has been read, set, or
        overwritten.

    Identifier
        A wrapper around variables, used to hold their potential
        non-existence (which is an Issue but not an Error).

    Type
        A symbolic representation of the variable's type.

    Literal
        Sometimes, we need a specialized representation of a literal value
        to be passed around. This is particularly important for accessing
        elements in an tuples.

    Name Map
        (Path x Fully Qualified Names) => States
"""

from pedal.tifa.tifa import Tifa
from pedal.report import MAIN_REPORT

NAME = 'TIFA'
SHORT_DESCRIPTION = "Finds common issues caused by students."
DESCRIPTION = '''Python Type Inferencer and Flow Analyzer (TIFA)

Tifa traverses an AST to detect common issues made by students.
'''
REQUIRES = ['Source']
OPTIONALS = []


def tifa_analysis(python_3=True, report=None):
    """
    Perform the TIFA analysis and attach the results to the Report.

    Args:
        python_3 (bool): Whether to expect a Python3 formated file, or Python
            2. This has slight nuance on certain AST elements.
        report (:class:`Report`): The Report object to attach results to.
            Defaults to :data:`MAIN_REPORT`.
    """
    if report is None:
        report = MAIN_REPORT
    t = Tifa(python_3=python_3, report=report)
    t.process_code(report['source']['code'])
    return t


__all__ = ['NAME', 'DESCRIPTION', 'SHORT_DESCRIPTION',
           'REQUIRES', 'OPTIONALS',
           'tifa_analysis', 'Tifa']
