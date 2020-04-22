Go through each of the following issues:

Student has syntax error
    > Doesn't crash the instructor code!
Student doesn't define function
    > We show them a message
Student overwrites a parameter
    > We handle that
Student uses a builtin function
    > We can prevent that
Avoid recursion
    > Cait does sophisticated matching
We write some simple unit tests

A thing we can see right off the bat is that we don't have to worry about errors in the student file.
There's no need to have complex try/catch blocks all over our instructor code.

python instructor.py submissions/syntax_error.py
pedal verify instructor.py submissions/