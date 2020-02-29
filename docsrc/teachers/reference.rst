.. _quick_reference:

Teacher Reference
=================

This section describes the functions and tools available within Pedal for the
benefit of an instructor authoring feedback. It does not attempt to exhaustively
document all the features available - for that, you should refer to the :ref:`full_api`.

Core Commands
-------------

Imported as::

    from pedal import set_success, compliment

.. function:: set_success(justification: str = None)

    Set this submission as correct/complete/successful. Typically resolved as overriding
    all other feedback. Often triggered as part of a conditional. You can optionally set
    an (internal) `justification` message for why this was triggered.

.. function:: compliment(message: str, value: number = 0, justification: str = None)

    Provides a `message` to the student complimenting them on something they did correctly.
    You can also specify a numeric `value` that will be added as partial credit.
    Finally, you can optionally set an internal `justification` message for why this was triggered.

.. function:: give_partial(value: number, justification: str = None)

    Increases the student's overall score by the numeric `value`.
    Finally, you can optionally set an internal `justification` message for why this was triggered.

CAIT
----

All the items in this guide may depend on one or more imports from the pedal package.
However, most of these should work with the following imports

.. code:: python

  from pedal.cait.cait_api import *
  from pedal.tifa import tifa_analysis

Note that you'll need to run tifa_analysis.

more often than not, you'll want to use `find_matches` as opposed to the `find_match` command used in this quick reference guide. The `find_match` function is used for brevity, but typicaly you'll use the following pattern

.. code:: python

  matches = find_matches("#instructor code")
  for match in matches:
    # do something

Also note that many of these items return a CaitNode; CaitNodes should mirror the built-in ast_node class except with added fields or functionality. In general it should be easier to work with CaitNodes as many additional operations and matching functionality are supported with CaitNodes.

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
.. code:: python

  match = find_match("_var_ = ___ + _var_")
  student_var = match['_var_']

Reference a function call
^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: python

  match = find_match("_var_ = _function_()")
  student_func_call = match['_function_']
  args = student_func_call.args #access list of arguments as CaitNodes
  keywords = student_func_call.keywords #access keyword arguments as CaitNodes

Reference a function definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: python

  match = find_match("def _my_func_():\n"
                     "    pass\n")
  student_func_def = match['_my_func_'] # root node of function definition

Note that by modifying this example, you can also check to see if the function is called, e.g.

.. code:: python

  match = find_match("def _my_func_():\n"
                     "    pass\n"
                     "_my_func_()")
  if match is None:
      gently("You haven't defined a function and used the function you defined!")

will look for a function definition followed by the usage of the function as an ast sibling (so same indentation level as definition

Subtree matching
^^^^^^^^^^^^^^^^

.. code:: python

  match = find_match("for _item_ in _list_:\n"
                     "    __exp__")
  match['__exp__'].find_match("# whatever submatch")

Normally CAIT will match to direct siblings. By using an expression, you can instead search everything contained in the body of the for loop, or other ast child nodes (see tutorial)

Finding Data types
^^^^^^^^^^^^^^^^^^

.. code:: python

  from pedal.tifa.type_definitions import *
  match = find_match("for _item_ in _list_:\n"
                     "    _sum_ = _sum_ + _item_")
  data_type = match['_sum_'].get_data_type()
  type(data_type) == NumType # checks if it the last type it took on

  data_state = match['_sum_'].get_data_state()
  data_state.was_type('NumType') # checks if _sum_ was a number at some point
  data_state.was_type(NumType) # equivalent to previous line

  match['_sum_'].was_type('NumType') # If you're only doing one access, you can use this



If you want to explore the data types yourself, recursively access the `trace` (a list of `State` objects) attribute of data_state and check each state's `type` attribute. For example

.. code:: python

  from pedal.tifa.type_definitions import *
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

Getting Output
^^^^^^^^^^^^^^
.. code:: python

    from pedal.sandbox.compatibility import get_output
    output = get_output()
    for item in output:
        print(item)  # Each line of output is given as a separate item in the list.
