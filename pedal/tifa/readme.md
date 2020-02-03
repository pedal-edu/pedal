PyTIFA is the Python Type Inferencer and Flow Analyzer, also called just Tifa.

Tifa is meant to be used on simple programs written in learning situations,
in order to provide type information and detect certain common issues.
It makes some very strong assumptions and doesn't support all language features.

Tifa is supported by Skulpt. This means that Tifa is a Python library that
can be passed in a string of Python source code in order to traverse its
AST using underlying JavaScript libraries. If that isn't confusing,
then we invite you to make pull requests.