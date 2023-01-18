.. _libraries:

Necessary Libraries
===================

A major design goal for Pedal was to limit third-party libraries. Unfortunately, we are still dependent on some
libraries in the Standard Library. Although that may not sound like a restriction, we are often interested in running
Pedal in non-Cpython versions of Python, such as Skulpt and MicroPython. This page attempts to document the libraries
we depend on, and why they are necessary. Where possible, we talk about workarounds.

Critical Standard Libraries
---------------------------

* ``sys``

    :py:mod:`pedal.sandbox`

        * ``modules`` to do monkey patching madness.
        * ``exc_info`` for exception stuff
        * ``settrace`` and ``gettrace`` for tracing
        * ``stdout`` for tracing rerouting

    :py:mod:`pedal.source.source`

        * ``exc_info`` for exception stuff

    :py:mod:`pedal.utilities`

        * ``stdout`` for exceptions
        * ``version_info`` for checking current system version

* ``os``

    :py:mod:`pedal.sandbox` and :py:mod:`pedal.utilities`

        * ``path`` is used for a few things

* ``dataclasses``

    :py:mod:`pedal.assertions`, :py:mod:`pedal.types`, :py:mod:`pedal.utilities`

        * ``fields`` and ``_FIELDS`` are used to inspect dataclass objects (should be try/catched!)

* ``functools``

    :py:mod:`pedal.assertions.organizers`

        * ``wraps`` is used out of convenience and for clarity, I think?

* ``re``

    :py:mod:`pedal.assertions`,:py:mod:`pedal.cait`, :py:mod:`pedal.sandbox`, :py:mod:`pedal.source`, :py:mod:`pedal.utilities`

        * ``search``, ``compile``, ``split``, ``MULTILINE``, ``sub`` are all necessary.

* ``ast``

    :py:mod:`pedal.assertions`, :py:mod:`pedal.cait`, :py:mod:`pedal.source`, :py:mod:`pedal.tifa`, :py:mod:`pedal.types`, :py:mod:`pedal.utilities`

        * ``parse``, but also like almost every single other class descending from ``Ast`` too. Oh, and ``NodeVisitor`` and ``iter_fields`` too.

* ``types``

    :py:mod:`pedal.cait`, :py:mod:`pedal.sandbox`, :py:mod:`pedal.types`

        * ``MethodType`` for dynamically creating methods (I wonder if this could be changed?)
        * ``ModuleType`` for dynamically creating modules

* ``io``

    :py:mod:`pedal.sandbox`

        * ``StringIO`` is necessary for handling mocked files, and capturing stdout

* ``unittest``

    :py:mod:`pedal.sandbox`

        * ``patch`` is necessary for more sophisticated patching used in the Sandbox and the Tracer

* ``traceback``

    :py:mod:`pedal.utilities.exception`

        * ``TracebackException`` and ``extract_tb`` are used to capture the full traceback info and reshape it.

* ``time``

    :py:mod:`pedal.sandbox.timeout`

        * ``time`` is used to get the current time for calculating the timeout

* ``math``

    :py:mod:`pedal.sandbox.result`

        * ``truncate`` needs to be imported and used in order to properly emulate it

* ``itertools``

    :py:mod:`pedal.sandbox.sandbox`

        * ``zip_longest`` is used as a convenience

* ``threading``

    :py:mod:`pedal.sandbox.sandbox`

        * ``Thread`` and ``_active`` are used to handle threading student code (which is usually necessary for properly handling timeouts)

* ``ctypes``

    :py:mod:`pedal.sandbox.timeout`

        * ``pythonapi``, ``c_long``, and ``py_object`` are used inside of threading the timeout stuff. I have no idea since that code is mostly stolen.

* ``bdb``

    :py:mod:`pedal.sandbox.tracer`

        * ``Bdb`` and ``BdbQuit`` are useful for tracing student code, but not critical.

* ``hashlib``

    :py:mod:`pedal.questions.setup`

        * depends on the ``md5`` function to translate users/questions into a replicable seed for consistent "random" question pools


* ``string``

    :py:mod:`pedal.utilities.comparisons`

        * ``punctuation`` is used in the string comparison function (could be hardcoded)

* ``numbers``

    :py:mod:`pedal.utilities.comparisons`

        * ``Number`` is used somehow?


Non-Critical Standard Libraries
-------------------------------

Most of the Environments require some various libraries (e.g., the Jupyter environment absolutely depends on
`nbformat`).


* `sys`

    :py:mod:`pedal.command_line`

        Uses `version_info`, `stdout`

    :py:mod:`pedal.environments`

        Uses `stderr`, `exc_info`, `argv`

* ``sqlite3``
* ``pickle``

Optional Third Party Libraries
------------------------------

These allow us to do some convenient things, but we don't *need* them.

* `coverage` - does some fancier tracing I believe?
* `tabulate`
* `tqdm`


Compatiblity
------------

Here is an attempt at figuring out compatibility with some popular CPython alternatives.

Skulpt
******

We support Skulpt via our own fork. Everything in Pedal works in our version of Skulpt because otherwise we couldn't
do BlockPy.

MicroPython
***********

These libraries seem to be sufficiently supported:

* ``re`` (although might need a specific MicroPython port?)
* ``io``
* ``time``
* ``truncate`` (although it might be ``trunc``? Need to investigate)
* ``hashlib``

These libraries might be a problem:

``sys``

    * ``sys.stdout`` is available
    * ``sys.modules`` is available, but might be missing "builting modules" (does that matter?)
    * ``sys.settrace`` is available, through a customized build! But what about ``sys.gettrace``? Doesn't seem to be implemented, but there might be workarounds...
    * ``sys.version_info`` is available, though might be slightly different?
    * ``sys.exc_info`` may **NOT** be available? Need to investigate, since that's a big deal breaker, I'm pretty sure.

``os``

    * ``path`` may **NOT** be available. Might be able to handle that other ways though?

``threading``

    * there is a ``_thread`` library with experimental support, so that might be sufficient?

``ctypes``

    * Since this is only used for timeout code, it might be related to what we need to do for ``threading``

These libraries are **NOT** available, and that's a deal-breaker until they are added:

* ``ast`` (entire thing seems to be missing)
* ``types`` (actually, I think its in the source code)
* ``unittest`` (key feature is missing)
* ``traceback`` (key features are missing)

These libraries are not available, but I suspect that we can work around:

* ``dataclasses`` (really not necessary unless you want students using dataclasses, which they can't!)
* ``functools`` (it's in the source code...)
* ``itertools``
* ``bdb``
* ``string`` (it's in the source code...)
* ``numbers``

The following features are CRITICAL to Pedal:

* Overriding sys.stdin, sys.stdout and sys.stderr not possible (well that's a deciding factor right there)

The following features would be DIFFICULT/PAINFUL to rewrite in Pedal:

* f-strings don’t support the !r, !s, and !a conversions
* Method Resolution Order (MRO) is not compliant with CPython
* When inheriting from multiple classes super() only calls one class
* User-defined attributes for functions are not supported (this one would be INCREDIBLY painful to rewrite)

The following features were convenient in Pedal, and could be avoided:

* f-strings don’t support concatenation with adjacent literals if the adjacent literals contain braces or are f-strings
* f-strings cannot support expressions that require parsing to resolve unbalanced nested braces and brackets
* Raw f-strings are not supported
* Failed to load modules are still registered as loaded

I am unclear if these will matter:

* Calling super() getter property in subclass will return a property object, not the value
* Error messages for methods may display unexpected argument counts
* Context manager __exit__() not called in a generator which does not run to completion
* User-defined attributes for builtin exceptions are not supported
* Attributes/subscr not implemented for `str`
* Subscript with step != 1 is not yet implemented¶
