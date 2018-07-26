Pedal
=====

A collection of tools to analyze student's work in a pipeline.

Important Concepts
==================

* *Report*: A collection of X and namespaces for the results of Tools.
* *Tool*: A system that can use a Report to add new information to the Report.
* *Resolver*: A system that can analyze a Report and create a relevant bit of output for another system (e.g., BlockPy, Web-CAT).

Tools
=====

TIFA
----

Tifa is a Type Inferencer and Flow Analyzer. Its goal is not to be a general purpose tool for doing so, but to be focused on simplistic code written in pedagogical settings. This means that it can make a lot of assumptions and forbid a lot of features. Further, it's primary job is not just to collect type information, but to detect issues in the code (e.g., a variable changes type, a variable is not read, a variable is defined in one scope then used in another).

CAIT
----

Capturer for AST Inclusion Trees. Its goal is to take a a desired AST and a target AST, and captures trees in the target ast that include the desired AST.

Mistakes
--------

A collection of code configuration patterns that represent common mistakes for students. These mistakes are grouped together by topics.

Rerun
-----
A simplistic system for running students' code under different circumstances (e.g., new stdin or arguments). Does not have many of the assurances that the Sandbox module does for executing student code more safely.

Rerun exists because not every environment supported by Pedal has access to certain code execution function (e.g., `exec` and `patch`). If you are using a regular Python engine (e.g., CPython) then you should consider using the `Sandbox` module.

Sandbox
-------

A sophisticated system for executing students' code under different circumstances. Improves upon the Rerun module by relying on the `exec` and `patch` tools of Python.

However, you should be aware that true sandboxing is impossible in a dynamic language like Python. Be sure that your environment has multiple lines of defense, such as proper file system permissions.

Resolvers
=========

FCFS
----

This resolver finds the highest priority message to deliver to the student, depending on a pre-established bit of logic for tools.