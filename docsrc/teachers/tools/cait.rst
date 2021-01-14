CAIT
----

All the items in this guide may depend on one or more imports from the pedal package.
However, most of these should work with the following imports

.. code-block:: python

    from pedal.cait.cait_api import *

Note that you'll need to run :py:func:`tifa_analysis` prior to certain commands.

More often than not, you'll want to use `find_matches` as opposed to the `find_match` command
used in this quick reference guide. The `find_match` function is used for brevity, but typically
you'll use the following pattern

.. code-block:: python

    matches = find_matches("#instructor code")
    for match in matches:
    # do something

Also note that many of these items return a CaitNode; CaitNodes should mirror the built-in
ast_node class except with added fields or functionality. In general it should be easier to work
with CaitNodes as many additional operations and matching functionality are supported with CaitNodes.

List of Pedal Data Types
^^^^^^^^^^^^^^^^^^^^^^^^
- BoolType
- DictType
- FunctionType
- LiteralBool
- LiteralNone
- LiteralNum
- LiteralStr
- NoneType
- NumType
- StrType
- TupleType
- UnknownType


Save and reference variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    match = find_match("_var_ = ___ + _var_")
    student_var = match['_var_']

Reference a function call
^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    match = find_match("_var_ = _function_()")
    student_func_call = match['_function_']
    args = student_func_call.args #access list of arguments as CaitNodes
    keywords = student_func_call.keywords #access keyword arguments as CaitNodes

Reference a function definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

  match = find_match("def _my_func_():\n"
                     "    pass\n")
  student_func_def = match['_my_func_'] # root node of function definition

Note that by modifying this example, you can also check to see if the function is called, e.g.

.. code-block:: python

  match = find_match("def _my_func_():\n"
                     "    pass\n"
                     "_my_func_()")
  if match is None:
      gently("You haven't defined a function and used the function you defined!")

will look for a function definition followed by the usage of the function as
an ast sibling (so same indentation level as definition

Subtree matching
^^^^^^^^^^^^^^^^

.. code-block:: python

  match = find_match("for _item_ in _list_:\n"
                     "    __exp__")
  match['__exp__'].find_match("# whatever submatch")

Normally CAIT will match to direct siblings. By using an expression, you can
instead search everything contained in the body of the for loop, or other ast
child nodes (see tutorial)

Finding Data types
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pedal.tifa.type_definitions import *
    match = find_match("for _item_ in _list_:\n"
                       "    _sum_ = _sum_ + _item_")
    data_type = match['_sum_'].get_data_type()
    type(data_type) == NumType # checks if it the last type it took on

    data_state = match['_sum_'].get_data_state()
    data_state.was_type('NumType') # checks if _sum_ was a number at some point
    data_state.was_type(NumType)   # equivalent to previous line
    data_state.was_type(int)       # equivalent to previous line

    match['_sum_'].was_type('NumType') # If you're only doing one access, you can use this



If you want to explore the data types yourself, recursively access the `trace` (a list of `State` objects) attribute of data_state and check each state's `type` attribute. For example

.. code-block:: python

    from pedal.types.definitions import *
    '''# Student Source Code
    var = 14
    var = 'String'
    '''
    match = find_match("_var_ = ___\n")
    data_state = match['_var_'].get_data_state()
    def print_types(data_state):
        print(data_state.type)
        if len(data_state.trace) > 0:
            print_types(data_state.trace[0])
    print_types(data_state)
    '''#Output
    StrType
    NumType
    '''
