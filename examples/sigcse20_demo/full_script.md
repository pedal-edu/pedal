# Hello Checker

We're going to run through a couple examples of how you might use Pedal to write
instructor grading scripts on a bunch of student submissions.
Exact details will vary depending on the environment you're integrating with,
but we'll be using the command line here after I've pip-installed Pedal.

First, let's make a grading script for a problem where a student has to print
out "Hello World". We'll start off by importing the Pedal library via its
Quick submodule, which gives access to our most commonly used tools.

```hello_checker.py
from pedal.quick import *
```

Then we call setup_pedal, which initializes the environment and gives us access
to a few useful pieces of data, including the students' Abstract Syntax Tree
and the data from when Pedal runs their code. That last return value is especially
important, its a function that we run when we've finished the rest of our script
to "resolve" all the feedback conditions and decide on the final feedback response.

```hello_checker.py
code, student, resolve = setup_pedal()

resolve()
```

We can run this instructor script from the command line and pass in a student file.

> correct.py

>>> python hello_checker.py hello_world/correct.py

The output down here shows that the student would normally be shown that they are
correct. This isn't all that interesting, though, since we don't actually have any
logic that verifies they have the right answer.

## Simple Output check

So let's add a simple check, to check that they actually printed something.

```hello_checker.py
if 'Hello world' not in student.output:
    gently("You have the wrong output", label="wrong_output")
```

Now we are checking the output from the student's program was run, and if it
does not have the desired string, then we are gently letting the student know
that their program was wrong. We label our feedback so we can keep track of it
later. If we try running this on a student submission where they print out the
wrong value.

> wrong_output.py

>>> python hello_checker.py hello_world/wrong_output.py

Then we have our message shown.
Now, this is not very sophisticated, it doesn't allow the student any flexibility
in terms of capitalization, whitespace, symbols. This other submission

> close_output.py

>>> python hello_checker.py hello_world/close_output.py

won't work for example, even though it followed my instructions. Well, we can use
one of our many helpful built-in tools to allow for more generous output checking.

```
if not student.printed('Hello world'):
```

That's going to ignore case, whitespace, and symbols.
When we run our code again, we find that are correct.

I made some changes to my instructor logic in this script, so I should really
run my old submissions and make sure that they are still correct.
Pedal can be run as a stand-alone script to verify that a directory of reference
submissions is outputing the right value.

> wrong_output.txt

>>> python hello_checker.py hello_world/wrong_output.py

I do have to have created expected output files for each of my submission cases,
but once I've done that I can easily find regressions.

>>> pedal verify hello_checker.py hello_world/

And this checks all the files and makes sure that they are still right.
This is using the builtin python unittest module, so it'd give me nice Diffs
if I failed any of those tests. But I passed them all, so I can feel relatively
confident that I haven't broken anything.

(Ad-libbed the syntax checker, forgot to have it prepared!)

# Summate Checker

Let's try a more sophisticated problem, where the user has to define a `summate`
function to sum up a list of values. We'll once again import and setup pedal.

```summate_checker.py
from pedal.quick import *

code, student, resolve = setup_pedal()
resolve()
```

We can start off by checking that they actually defined the function.
There's a few ways we could do this, such as by using the Toolkit submodule's 
match_signature function.

```summate_checker.py
if match_signature('summate'):
    ...
```

But instead I want to show off CAIT, which is a tool for flexibly searching the
students' code simply by writing valid Python code. We'll demand that the student
have defined a function with any number of parameters and anything in the body,
using CAIT's wildcard expression.

```summate_checker.py
match = find_match("""
def summate():
    __expr__
""")
```

If this doesn't match, then we can print out a little bit of feedback.

```summate_checker.py
if not match:
    explain("You have not defined the function", label="function_missing")
```

Let's try running this on a student submission. 

> missing_function.py

This student seems to have the right code, but they've defined a function named
add_up instead of summate. So it'll give them that feedback message from before.

>>> python summate_checker.py summation/missing_function.py

Of course, it's not enough to just have the function with the right name, we
need to call it and make sure that we have the right result. We can write a 
unittest using Pedal's assertion syntax.

```summate_checker.py
else:
    assertEqual(student.call('summate', [1, 3, 5]), 9)
```

This will safely call the students' function and pass in the given arguments,
ensuring that the right result is returned. Let's try running it on a correct
solution.

> correct.py

>>> python summate_checker.py correct.py

Okay, seems good. Now what if the student had made a very small mistake, what
if they counted the number of items instead of a summation? They added 1 in
each loop instead of the iteration variable.

> count_vs_sum.py

>>> python summate_checker.py count_vs_sum.py

Notice that this doesn't give a traceback with instructor code, it just shows
the student what the instructor ran, what they got, and what they expected.
It looks a little better in an environment that supports HTML.

Okay, so we have ways to check the correctness, so we can start thinking of
some trickier situations. For example, a common mistake that about 2/3 of my
students make the first time they write a function is to try to re-initialize
parameters.

> overwrote_params.py

See here on line 2, they're incorrectly overwrote those values before they were
even used. Even worse, they're using the exact value from our unit tests, so
if we didn't have any others then it wouldn't detect the mistake. But, here's
where another built-in Pedal feature can help. We've written a simple static analyzer
named TIFA that will analyze the students' code and will give feedback on
mistakes like this.

>>> python summate_checker.py overwrote_params.py

TIFA has a lot of conditions that it can handle, including variables that aren't
read or defined, or when you incorrectly try to combine types. If you don't trust it,
you can also just turn it off entirely.

Let's consider another common student mistake. They see the problem is to add up
a list of numbers, so they google for how to do that in Python. They find a stackoverflow
post that says to use the built-in sum function, so they just write...

> used_builtin.py

Obviously, that's not what we want them to do, but we can prevent the use of
built-ins with a helpful function from Pedal's Toolkit.

```summate_checker.py
from pedal.toolkit.utilities import prevent_builtin_usage
# ...
prevent_builtin_usage('sum')
```

And now they will get feedback about not using that function.

Okay, one more example, this time we'll use CAIT in a more sophisticated way.
An issue that sometimes comes up with new students is that they try to incorporate
the function they are defining into the body of the function, basically accidentally
causing infinite recursion.

> recursion.py

We can add a second submatch on our existing match object to detect if the
summate function is called inside the function's definition.

```
if match['__expr__'].find_match("summate()"):
    explain("You are doing recursion, don't do that!", label="used_recursion")
else:
    ....
```

>>> python summate_checker.py recursion.py

And we could write a bit more explanation or guidance for the student, give
them a hint or something. But this will suffice as a start.

Pedal has a lot more features than just the ones we've shown here.
But these are some of the more core, exciting ones.

(Hide prompt in VS Code)
>>> Function Prompt { "$( ( get-item $pwd ).Name )>" }