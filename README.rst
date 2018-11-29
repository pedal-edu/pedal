Pedal
=====

A collection of tools to analyze student's work in a pipeline. Pedal not only provides some of these tools, but it provides a *framework* around those tools.

Important Concepts
==================

.. image:: docs/_static/pedal-overview.png

* *Report*: A collection of Feedback and a namespace for the results of Tools, accessible by the Tool name. Reports can be generated imperatively (using the default Report, similar to MatPlotLib) or by explicitly creating and passing Report objects.
* *Tool*: A system that can read and write to a Report, building on the work of previous Tools.
* *Resolver*: A system that can analyze a Report and create a relevant bit of output for another system (e.g., BlockPy, Web-CAT).
* *Feedback*: A structured representation of content to be delivered to a student in response to their submission of work.

We base our idea of "Feedback" on concepts established by Narciss 2006. Our Feedback objects are composed of up to 7 components:

* result (bool): Whether or not this feedback is associated with the learner completing the task ("Success!")
* performance (float): A relative amount that this feedback contributes to the students' performance (think in terms of partial credit, like "Triggering this feedback is worth 20%").
* misconceptions (Component): A description of the misconception that is believed to be in the student's mind, or perhaps the relevant concept from the material that should be associated with this. ("Variables must be initialized before they are used.")
* mistakes (Component): A description of the error or bug that the student has created ("NameError on line 5: sum has not been defined")
* hints (Component): A suggestion for what the student can do ("Initialize the sum variable one line 1")
* constraints (Component): A description of the task requirements or task type that the student has violated ("You used a for loop, but this question expected you to use recursion.")
* metacognitives (Component): A suggestion for more regulative strategies ("You have been working for 5 hours, perhaps it is time to take a break?")

One of these components is described by the following union type, where a Component is one of:

* A str field representing renderable text for a student
* An object with a "message (str)" field of renderable text for a student, along with whatever other fields are useful (e.g., the line number of the error)
* A list of Components

Additionally, a given Feedback object has the following metadata:

* label (str): An internal name for this specific piece of feedback. This is particularly useful for us for research purposes (we currently show it in italics as part of the message)
* tool (str): An internal name for indicating the tool that created this feedback (e.g., "tifa" or "source")
* category (str): A human-presentable name showable to a student (this is like the "Analyzer Error" message in the top left of our BlockPy boxes).
* priority (str): An indication of how important this feedback is. Might be "high/medium/low" or the name of a category to supersede.

Tools
=====

Source
------

.. code:: python

  from pedal.source import set_source
  STUDENT_CODE = "message='Hello World'\nprint(message)"
  set_source(STUDENT_CODE)

One of the simplest tools, the Source tool provides a function for attaching source code to a Report. It is a requirement for any tool that wants to do code analysis. But notice that this tool is not required in general - you could find other ways to attach code (e.g., a History tool that attaches all previous code written) or other aspects of the students' performance (e.g., a Demographics tool to attach bio-data about the student).

TIFA
----

Tifa is a Type Inferencer and Flow Analyzer. Its goal is not to be a general purpose tool for doing so, but to be focused on simplistic code written in pedagogical settings. This means that it can make a lot of assumptions and forbid a lot of features. Further, it's primary job is not just to collect type information, but to detect issues in the code (e.g., a variable changes type, a variable is not read, a variable is defined in one scope then used in another).

CAIT
----

.. code:: python

    from pedal.cait import parse_program, find_matches
    parse_program()
    matches = find_matches("_var_ = __expr__")

Capturer for AST Inclusion Trees. Its goal is to take a a desired AST and a target AST, and captures trees in the target ast that include the desired AST. A metaphor might be "Regular Expressions for source code".

For the following explanations, source refers to the code you are trying to match to:

`find_matches` takes regular python code, but creates special placeholders shown below
.. code:: python

    ___

The triple underscore is used as a wild match card. It will match to any node or subtree and toss out all relevant information

.. code:: python

    _var_

is a place holder for variables, denoted by single under scores. Many instructor variables are allowed to map to one variable in source, but each variable in source can only map to one instructor variable. Note that these aren't bidirectional mappings
example:

.. code:: python

    # source 1
    var1 = var1/var2
    # source 2
    var1 = var2/var2
    # matcher 1
    match = find_match("_var1_ = _var1_/_var_2")
    # matcher 2
    match = find_match("_var1_ = _var2_/_var_2")
    
In the example above, matcher 1 would find source 1 but wouldn't find source 2 because source variable `var2` is being mapped to both `_var1_` and `_var2_`. However, matcher 2 would find both source 1 and source 2 because while matcher 2's `_var2_` will map to both source 2's `var1` and `var2`, source 2's `var2` only maps to matcher 2's `_var2_` If a variable name is not surrounded by single underscores, Cait will try to match the exact variable name. Note: this only works for AST nodes that are Name nodes and FuncDefinition nodes. Note that the matcher will save these variables/names for later reference (discussed below)

.. code:: python

    __expr__

is a place holder for subtree expressions. An expression is denoted by a double underscore before and after the name of the expression. Example:


.. code:: python

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
        counter = count + 1
        running_avg.append(summer/counter)

In this example, matches would return a list of two matches, as shown above (match 1 and match 2). Note that the matcher will save these expressions for later reference (discussed below). Another special note is that unlike the variable place holder, each expression reference is expected to only be used once in any given match. The following example matcher will produce undefined behavior:

.. code:: python

    # matcher 1
    matches = find_matches("for ___ in ___:\n"
                           "    __expr1__\n"
                           "    __expr1__")


Retrieving variables, functions, and expressions is another operation supported in Cait

.. code:: python

    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__\n"
                           "__expr2__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            __expr2__ = match["__expr2__"]

The code above shows how to retrieve expressions and variables. The expressions (`__expr__` and `__expr2__`) will return AST nodes with expanded functionality from the built in ast node class.

Retrieval of variables and functions will return a list of AstSymbol objects. These AstSymbol objects will also have a reference to the specific Name or FuncDefinition AST node that the symbol matched to (details in ast_map.py). So there should be one for every time the variable/function definition ocurred in code. Note that overlapping variable and function names in instructor will cause conflicts as they are considered to be the "same symbol" with respect to CAIT. This can allow checks such as detecting if students overwrite a function that they have written.

Finally, for subtree matching, you can use the `find_submatches` function.

.. code:: python

    def find_submatches(ins_expr, std_expr, as_expr=True, is_mod=False, cut=False):
        """Finds ins_expr in std_expr
        :param ins_expr: the expression to find (str that MUST evaluate to a Module node with a single child)
        :param std_expr: source subtree
        :param as_expr: whether the child is an expression ast node or not
        :param is_mod: currently hack for multiline sub matches, experimental
        :param cut: flag for cutting off root until a branch occurs, should tyipcally be set to true
        :return: a list of matches or False if no matches found
        """

The `find_submatches` function allows you to perform deep searches, such as if you are looking for a specific expression in a subtree and you don't care where that expression is in that subtree. For example:

.. code:: python

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
    submatch = find_expr_sub_matches("_var1_ = _var2_ + _var1_", __expr1__, cut=True)

In the example above, `__expr1__` will match to the inner body of the for loops in source 1 and source 2. The `submatch` variable would then in both cases, extract the `summer = summer + item` from both sources, returning the same type of list as `find_matches`.

A final note for that example, note that some operations are expected to be commutative. Currently only addition and multiplication are supported as commutative operators. This commutativity currently unintelligently allows either ordering for the subtrees of the addition or multiplication ast nodes, and in the case as above, would return two matches, one for `_var1_ = _var2_ + _var1_` and one for `_var1 = _var1_ + _var2_`. If they are not commutative (e.g. because of a function call that changes state), Cait currently doesn't detect such cases

Mistakes
--------

A collection of code configuration patterns that represent common mistakes for students. These mistakes are grouped together by topics.

Toolkit
-------

A collection of helper functions to analyze student code, such as detecting incorrectly closed files, preventing the use of certain operators or literals, and unit testing functionality.

Sandbox
-------

A sophisticated system for executing students' code under different circumstances. Relies on the `exec` and `patch` tools of Python to prevent students from escaping their namespace.

However, you should be aware that true sandboxing is impossible in a dynamic language like Python. Be sure that your environment has multiple lines of defense, such as proper file system permissions.

Resolvers
=========

FCFS
----

This resolver finds the highest priority message to deliver to the student, depending on a pre-established bit of logic for tools.

Oter resolvers are possible - we could find the first, or deliver more than one (grouped using HTML formatting).
