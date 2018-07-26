'''
A package for analyzing student code.
'''

'''
How do we best support instructors?

For BlockPy, we need to port the Feedback module over to pure python, I think.
    Error types
    Success types
    Compliment
    
    It is not BlockPy's responsibility to build the feedback, just to render it.
        error(type, name, message, line)    
        error("Algorithm", "Action after return", "No actions can be performed after returning.", 45)
        error("Syntax", "Bad Input", "Unclosed parentheses", 133)
        error("Runtime", "TypeError", "You cannot add a string and an integer", 23)
    
'''


'''
import iteration_context as ins_cont
ins_cont.wrong_list_is_constant_8_2()
ins_cont.missing_list_initialization_8_2()
ins_cont.wrong_list_length_8_2()
ins_cont.list_all_zeros_8_2()
set_success()
'''