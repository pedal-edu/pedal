TIFA
====


TIFA is a powerful tool, but not one that comes with much configuration.

Imported as::

    from pedal.tifa import tifa_analysis

.. function:: tifa_analysis()

    Runs the TIFA analysis engine on the current submission. Any issues identified
    will be attached to the report; most of them are displayed by default.

The following section breaks down the existing set of TIFA issues.

.. feedback_function:: pedal.tifa.feedbacks.action_after_return

.. feedback_function:: pedal.tifa.feedbacks.return_outside_function

.. feedback_function:: pedal.tifa.feedbacks.multiple_return_types

.. feedback_function:: pedal.tifa.feedbacks.write_out_of_scope

.. feedback_function:: pedal.tifa.feedbacks.unconnected_blocks

.. feedback_function:: pedal.tifa.feedbacks.iteration_problem

.. feedback_function:: pedal.tifa.feedbacks.initialization_problem

.. feedback_function:: pedal.tifa.feedbacks.possible_initialization_problem

.. feedback_function:: pedal.tifa.feedbacks.unused_variable

.. feedback_function:: pedal.tifa.feedbacks.overwritten_variable

.. feedback_function:: pedal.tifa.feedbacks.iterating_over_non_list

.. feedback_function:: pedal.tifa.feedbacks.iterating_over_empty_list

.. feedback_function:: pedal.tifa.feedbacks.incompatible_types

.. feedback_function:: pedal.tifa.feedbacks.parameter_type_mismatch

.. feedback_function:: pedal.tifa.feedbacks.read_out_of_scope

.. feedback_function:: pedal.tifa.feedbacks.type_changes

.. feedback_function:: pedal.tifa.feedbacks.unnecessary_second_branch

.. feedback_function:: pedal.tifa.feedbacks.else_on_loop_body

.. feedback_function:: pedal.tifa.feedbacks.recursive_call

.. feedback_function:: pedal.tifa.feedbacks.not_a_function

.. feedback_function:: pedal.tifa.feedbacks.incorrect_arity

.. feedback_function:: pedal.tifa.feedbacks.multiple_return_types

.. feedback_function:: pedal.tifa.feedbacks.module_not_found

.. feedback_function:: pedal.tifa.feedbacks.append_to_non_list
