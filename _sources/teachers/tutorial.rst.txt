.. _tutorial:

Teacher Tutorial
================

.. warning:: This document is out of date, please refer to the QuickStart and Reference pages for now!

Using Pedal
###########
Pedal is a collection of tools to analyze student's work in a pipeline.
Pedal not only provides some of these tools, but it provides a *framework* around those tools.
In this tutorial we go over the important concepts of Pedal, review each of the tools that compose Pedal,
and then give practical examples of how to use Pedal.

Tools
-----

Source
^^^^^^

.. code-block:: python

  from pedal.source import set_source
  STUDENT_CODE = "message='Hello World'\nprint(message)"
  set_source(STUDENT_CODE)

One of the simplest tools, the Source tool provides a function for attaching source code to a Report. It is a requirement for any tool that wants to do code analysis. But notice that this tool is not required in general - you could find other ways to attach code (e.g., a History tool that attaches all previous code written) or other aspects of the students' performance (e.g., a Demographics tool to attach bio-data about the student).

TIFA
^^^^

Tifa is a Type Inferencer and Flow Analyzer. Its goal is not to be a general purpose tool for doing so, but to be focused on simplistic code written in pedagogical settings. This means that it can make a lot of assumptions and forbid a lot of features. Further, it's primary job is not just to collect type information, but to detect issues in the code (e.g., a variable changes type, a variable is not read, a variable is defined in one scope then used in another).

CAIT
^^^^

.. code-block:: python

    from pedal.cait import parse_program, find_matches

    ast = parse_program()
    if ast.find_all("For"):
        pass # For loop detected!

    matches = find_matches("_var_ = __expr__")

.. code-block:: python

    from pedal.source import set_source
    from pedal.cait import parse_program, find_matches
    from pedal.tifa import tifa_analysis # optional
    set_source("string_of_student_code")
    tifa_analysis() # optional, use for flow/data analysis
    parse_program()
    matches = find_matches("_var_ = __expr__")

Capturer for AST Inclusion Trees. Its goal is to take a desired AST and a target AST, and captures trees in the target ast that include the desired AST. A metaphor might be "Regular Expressions for source code".

For the following explanations, source refers to the code you are trying to find trees in:

`find_matches` takes regular python code, defined as "instructor code", but creates special placeholders shown below

.. code-block:: python

    ___

The triple underscore is used as a wild match card. It will match to any node or subtree. If you wish to access such data, you should use expressions instead (described further down)

.. code-block:: python

    _var_

is a place holder for variables, denoted by single under scores. Many source variables are allowed to match to one matcher variable, but each matcher variable code can only match to one source variable. Note this implies that these aren't bidirectional mappings.

example:

.. code-block:: python

    # Matcher 1
    _var1_ = _var2_/_var3_

    # Matcher 2
    _var1_ = _var2_/_var2_

    # Source 1
    x = y/x

    # Source 2
    x = y/y

    # Source 3
    x = x/x

Matcher 1 will map to Source 1, Source 2, Source 3. In Source 1, source variable x matches to both _var1_ and _var3_, however, _var3_ only matches to source variable x (and similarly _var1_ only matches to source variable x). Similarly this applies to Source 2 and 3.

Matcher 2 will NOT map to Source 1 and will only map to Source 2, Source 3 because for source 1, _var2_ would not be able to match to both source variable x AND source variable y.

In more simple terms, if you are familiar with regular expressions, these variable markers work similarly to groupings in regular expressions. The values of the groups marked denoted by say $1 and $2 might be the exact same string internally, but are referenced by two different groups in practice. e.g. "fun,fun," can map to (.*,)(.*,), which gets to two different groups, $1 and $2.

.. code-block:: python

    __expr__

is a place holder for subtree expressions. An expression is denoted by a double underscore before and after the name of the expression. Example:


.. code-block:: python

    # source 1
    summer = 0
    counter = 0
    running_avg = []
    for item in i_list:
        summer = summer + item
        counter = count + 1
        running_avg.append(summer/counter)
    # matcher 1
    matches = find_matches("for ___ in ___:\n"
                           "    __expr1__\n"
                           "    __expr2__")
    # match 1
    for item in i_list:
        summer = summer + item
        counter = count + 1
    # match 2
    for item in i_list:
        summer = summer + item
        running_avg.append(summer/counter)
    # match 2
    for item in i_list:
        counter = count + 1
        running_avg.append(summer/counter)

In this example, matches would return a list of three matches, as shown above (match 1, match 2, and match 3). Note that the matcher will save these expressions for later reference (discussed below). Another special note is that unlike the variable place holder, each expression reference is expected to only be used once in any given match. The following example matcher will produce undefined behavior:

.. code-block:: python

    # matcher 1
    matches = find_matches("for ___ in ___:\n"
                           "    __expr1__\n"
                           "    __expr1__")


Retrieving variables, functions, and expressions is another operation supported in Cait

.. code-block:: python

    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__\n"
                           "__expr2__")
    for match in matches:
        # _item_ = match["_item_"][0] is nearly equivalent
        _item_ = match["_item_"]
        __expr__ = match["__expr__"]
        __expr2__ = match["__expr2__"]

The code above shows how to retrieve expressions and variables. The expressions (`__expr__` and `__expr2__`) will return AST nodes with expanded functionality from the built in ast node class.

Retrieval of variables and functions will return an AstSymbolList, which can be accessed as a list of AstSymbols or as the first AstSymbol in the list. These AstSymbol objects will also have a reference to the specific Name or FuncDefinition AST node that the symbol matched to (details in ast_map.py). So there should be one for every time the variable/function definition occurred in code. Note that overlapping variable and function names in instructor code will cause conflicts as they are considered to be the "same symbol" with respect to CAIT. This can allow checks such as detecting if students overwrite a function that they have written.

Finally, for subtree matching, you can use the `find_matches` function of the expression. When calling `find_matches` on an expression, you can perform deep searches, such as if you are looking for a specific expression in a subtree and you don't care where that expression is in that subtree. For example:

.. code-block:: python

    # source 1
    summer = 0
    for item in i_list:
        summer = summer + item

    # source 2
    summer = 0
    for item in i_list:
        if True:
            if True:
                if True:
                    summer = summer + item

    # matcher 1
    matches = find_matches("for ___ in ___:\n"
                           "    __expr1__\n")
    __expr1__ = match["__expr1__"]
    submatches = __expr1__.find_matches("_var1_ = _var2_ + _var1_")

In the example above, `__expr1__` will match to the inner body of the for loops in source 1 and source 2. The `submatches` variable would then in both cases, extract the `summer = summer + item` from both sources, returning the same type of list as `find_matches`.

A final note for that example, note that some operations are expected to be commutative. Currently only addition and multiplication are supported as commutative operators. This commutativity currently unintelligently allows either ordering for the subtrees of the addition or multiplication ast nodes, and in the case as above, would return two matches, one for `_var1_ = _var2_ + _var1_` and one for `_var1 = _var1_ + _var2_`. If they are not commutative (e.g. because of a function call that changes state), Cait currently doesn't detect such cases

Finding AST Elements
^^^^^^^^^^^^^^^^^^^^

`CAIT` is a "Capturer for AST Inclusion Trees", a fancy way of saying it can be used to access the
AST of the learners' code. If the code failed to parse, `CAIT` functions are still safe to run - they
will not cause exceptions, just return no results. `CAIT` has almost no `Feedback Functions`; instead, it
supports `Feedback Condition` authoring through two mechanisms.

The first major feature is `find_all`:

.. code-block:: python

    if ast.find_all("For"):
        gently("It looks like your code is using a `for` loop; don't do that!", "used_for_loop")

The `find_all` function returns a list of `CaitNodes`, which represent elements of the AST.
You can access attributes of these nodes; we recommend you refer to the
`GreenTreeSnakes <https://greentreesnakes.readthedocs.io/en/latest/nodes.html>`_ documentation
for more information about what is available.

.. code-block:: python

    loops = ast.find_all("For")
    for loop in loops:
        if loop.target.name == "Tuple":
            gently("You have a `for` loop with multiple targets, don't do that!", "for_loop_multiple_targets")

Mistakes
^^^^^^^^

A collection of code configuration patterns that represent common mistakes for students. These mistakes are grouped together by topics.

Toolkit
^^^^^^^

A collection of helper functions to analyze student code, such as detecting incorrectly closed files, preventing the use of certain operators or literals, and unit testing functionality.

Sandbox
^^^^^^^

A sophisticated system for executing students' code under different circumstances. Relies on the `exec` and `patch` tools of Python to prevent students from escaping their namespace.

However, you should be aware that true sandboxing is impossible in a dynamic language like Python. Be sure that your environment has multiple lines of defense, such as proper file system permissions.

Resolvers
^^^^^^^^^

FCFS
""""

This resolver finds the highest priority message to deliver to the student, depending on a pre-established bit of logic for tools.

Oter resolvers are possible - we could find the first, or deliver more than one (grouped using HTML formatting).

