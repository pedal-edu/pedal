.. _integrations:


Autograder Integrations
=======================

Pedal is not tied to a single autograding platform, our vision is that it should be usable anywhere. This
is largely achieved through "environments", which can be set as command line parameters to reconfigure Pedal
for the desired autograding platform. If you want to see a new platform, then please raise an Issue on our GitHub!

VPL
---

You will need to create an instructor control script (e.g., `ics.py`), and upload it along with a `vpl_evaluate.sh` file:

.. code-block:: console
    :caption: vpl_evaluate.sh

    # Run the environment variable initializer to get access to its variables
    source ./vpl_environment.sh
    echo "#!/bin/bash" > vpl_execution
    echo "python3.6 -m pedal grade ics.py $VPL_SUBFILE0 --environment vpl">> vpl_execution
    chmod +x vpl_execution

You should configure the assignment as follows:

* Include the `ics.py` file in the "Files to keep when running"
* Under "Execution Options", enable Evaluate and Automatic Grade.

When you use the VPL environment, you can expect the following:

* Most HTML tags are not available; only headers and preformatted text blocks are available.

GradeScope
----------

You will need to create an instructor control script (e.g., `ics.py`) and upload it along with the following files:

.. code-block:: console
    :caption: setup.sh

    python3 -m pip install pedal
    # Or use the development version of Pedal
    # python3 -m pip install git+git://github.com/pedal-edu/pedal.git
    # We also have these additional curriculum libraries available
    # python3 -m pip install git+git://github.com/pedal-edu/curriculum-sneks.git
    # python3 -m pip install git+git://github.com/pedal-edu/curriculum-ctvt.git

.. code-block:: console
    :caption: run_autograder

    #!/usr/bin/env bash
    # Runs the first python file that the student submitted
    files=( /autograder/submission/*.py )
    pedal grade \
            /autograder/source/ics.py \
            "${files[0]}" \
            --environment gradescope \
            --output "/autograder/results/results.json"

An example Instructor Control Script looks like this:

.. code-block:: python
    :caption: ics.py

    from pedal import *

    # Set the maximum score for the assignment here
    set_maximum_score(100)

    # ...

By default, the GradeScope environment will:

* Run both TIFA and the student's code (the first file it finds)
* Produce HTML output
* Only show the highest priority feedback message, rather than all possible feedback

.. image:: ../_static/gradescope_example.png

BlockPy
-------

BlockPy comes preloaded with Pedal. No special configuration is required!

Web-CAT
-------

We have not tried the latest version of Pedal on Web-CAT. However, we believe that it should be possible to install
Pedal and have it generate appropriate documentation, based on our success with an earlier version. If you are
interested in this effort, please check our GitHub Issues!

Jupyter Notebooks
-----------------

Jupyter Notebook integration has been achieved, but we have not really prepared this for other people to use.
If you are interested, then you will need to make sure that the Jupyter server preloads the Grade Magic command we
have created. From there, you can create custom notebooks with the instructor grading code at the bottom. We wrote
a `simple extension <https://github.com/acbart/jn-student-toolbar>`_` to hide these cells (along with
other interface changes).