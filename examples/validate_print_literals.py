from pedal import *

prevent_operation("/", message="Don't use division in this problem, use the actual decimal value (`0.01`).")

ensure_function_call('print', at_least=3)
ensure_literal_type(int)
ensure_literal_type(float,
                    message="You need to have a decimal value (a `float`) in your code, in order to represent the value of a Penny. If a Penny is worth 1/100 of a dollar, how much is that as a decimal?")
ensure_literal_type(str)

ensure_ast('Num', at_least=2)
prevent_ast('Num', at_most=2)
ensure_ast('Str', at_least=1)
prevent_ast('Str', at_most=1)

if not get_output():
    gently("You are not printing.", label="not_printing", title="Not Printing")

prevent_literal(.1, message="A penny is worth `.01` dollars, not `.1` dollars (that would be a dime).")
prevent_literal(1,
                message="A penny is worth `.01` dollars, not `1` dollars (that would be in cents instead of in dollars).")

ensure_literal(7, message="You need to have a literal value representing the number of days in a week.")
# ensure_literal("triangle", message="You need to have a literal value representing a shape with three sides.")
ensure_literal(.01, message="You need to have a literal value representing the value of a Penny (1 cent) in dollars.")

assert_output_contains(student, "7",
                       message="You need to print out the literal value representing the number of days in a week.")
assert_output_contains(student, "triangle",
                       message="You need to print out the literal value representing a shape with three sides.")
assert_output_contains(student, ".01",
                       message="You need to print out the literal value representing the value of a Penny (1 cent) in dollars.")

assert_not_output_contains(student, "6",
                           message="Change the literal value `6` to instead represent the number of days in a week.")
assert_not_output_contains(student, "square",
                           message="Change the literal value `square` to instead represent a shape with three sides.")
assert_not_output_contains(student, ".05",
                           message="Change the literal value `.05` to instead represent the value of a Penny (1 cent) in dollars.")