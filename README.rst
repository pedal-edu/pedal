Pedal
=====

A collection of tools to analyze student's work in a pipeline. Pedal not only provides some of these tools, but it provides a *framework* around those tools.

Important Concepts
==================

![Overview of Pedal Framework](docs/_static/pedal-overview.png)

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

```python
from pedal.source import set_source
STUDENT_CODE = "message='Hello World'\nprint(message)"
set_source(STUDENT_CODE)
```

One of the simplest tools, the Source tool provides a function for attaching source code to a Report. It is a requirement for any tool that wants to do code analysis. But notice that this tool is not required in general - you could find other ways to attach code (e.g., a History tool that attaches all previous code written) or other aspects of the students' performance (e.g., a Demographics tool to attach bio-data about the student).

TIFA
----

Tifa is a Type Inferencer and Flow Analyzer. Its goal is not to be a general purpose tool for doing so, but to be focused on simplistic code written in pedagogical settings. This means that it can make a lot of assumptions and forbid a lot of features. Further, it's primary job is not just to collect type information, but to detect issues in the code (e.g., a variable changes type, a variable is not read, a variable is defined in one scope then used in another).

CAIT
----

```python
from pedal.cait import parse_program, find_matches
parse_program()
matches = find_matches("_var_ = __expr__")
```

Capturer for AST Inclusion Trees. Its goal is to take a a desired AST and a target AST, and captures trees in the target ast that include the desired AST. A metaphor might be "Regular Expressions for source code".

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