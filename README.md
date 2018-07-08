# python-analysis
A collection of tools to analyze student's Python source code

# TIFA

Tifa is a Type Inferencer and Flow Analyzer. Its goal is not to be a general purpose tool for doing so, but to be focused on simplistic code written in pedagogical settings. This means that it can make a lot of assumptions and forbid a lot of features. Further, it's primary job is not just to collect type information, but to detect issues in the code (e.g., a variable changes type, a variable is not read, a variable is defined in one scope then used in another).

# MDF (Name?)

A tool for detecting the absence or presence of instructor-authored patterns in student source code, using a tree inclusion algorithm. Also able to handle certain kinds of constraints.

#CAIT
Capturer for AST Inclusion Trees. Its goal is to take a a desired AST and a target AST. CAIT captures trees in the target ast that include the desired AST.

# Feedback Dispatch (Name?)

Given the results of execution and analysis, this tool determines what kind of feedback to deliver to the student.

# Python-PEML (Name?)

A tool for processing PEML files. Currently converts to BlockPy's instructor API.
