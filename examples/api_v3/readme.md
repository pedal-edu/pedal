This directory contains examples of the V3 Pedal API.


# The Examples

```
$> pedal debug simple_test.py student_code.py --environment blockpy
$> pedal debug unit_test_examples.py student_code.py --environment blockpy
```


# Running Code

This section has some scattered notes about different ways to run code with
Pedal.

## Run File Directly

You can run this file directly on a student file to see the output.

```
$> python instructor.py student.py
```

## Grade with Pedal

Or run with Pedal to get more extensive options.

```
$> pedal grade instructor.py student.py
```

## Verify Directory

You can verify an instructor grading script using a directory
of student submissions alongside their expected output.

```
$> pedal verify instructor.py submissions/
```

## BlockPy Script

BlockPy grading scripts, like some other environments, surround their code
with boilerplate. When running these scripts from the command line, they should
be used slightly differently.

```
$> pedal grade instructor.py student.py --environment blockpy
```

This will automatically load the BlockPy environment:

* Sets up the student's submission (filename and code)
* Loads in inputs
* Runs the student's code and makes the sandbox available as `student`
* Runs `tifa_analysis`
* Runs the resolver afterwards



#

When you first import pedal, it does some quick inspection to figure out
what kind of circumstance it's being loaded into. It checks command line
arguments and... what else?


## No environment

```
$> python instructor.py student.py
```

Automatically infers the arg to be student submission, attaches it to report.
Need to manually run the following

```
from pedal import *
verify()
tifa_analysis()
student = run()
...
final = resolve()
```

## Custom environment

```
$> python instructor.py student.py --environment blockpy
```

You automatically get student from the import, and verify/tifa_analysis are
already run.

You could also manually set the environment by starting the file with
```
from pedal.environments.blockpy import *
```

If you try to access certain builtins expecting them to be there, and they
aren't, then it can ask "Perhaps you meant to set an environment?"

## As library

So what if the user is just importing pedal in order to use a Tool?
    Well, no environment, so nothing gets auto-run. But what if their tool was
    using one of our parameters?

Perhaps in this special case, they could just clear out the sysargs

Or even just set a special ENVIRON variable.

We could even provide a special version of the package to handle this, if
we want to be fancy.

```
import pedal_lib
```

And then that module handles the weird environ setting

So it's just

```
import os
os.environ['PEDAL_AS_LIBRARY'] = True
from pedal.cait import find_match
```