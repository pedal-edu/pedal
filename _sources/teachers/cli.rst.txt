.. _cli:

Command-Line Interface
======================

In addition to being a library, Pedal also provides a command-line interface (CLI) for analyzing student code.
This is useful for batch processing or on individual submissions (e.g., through a platform like GradeScope or VSCodeEdu).
For specific integrations, see the :ref:`integrations` section.

Command Line Modes
------------------

.. autoclass:: pedal.command_line.modes.SandboxPipeline

.. autoclass:: pedal.command_line.modes.RunPipeline

.. autoclass:: pedal.command_line.modes.FeedbackPipeline

.. autoclass:: pedal.command_line.modes.GradePipeline

.. autoclass:: pedal.command_line.modes.StatsPipeline

.. autoclass:: pedal.command_line.modes.VerifyPipeline

.. autoclass:: pedal.command_line.modes.DebugPipeline

File Formats
------------

Pedal can read and write several file formats. The most common are:

- Python files (``.py``)
- Folders containing Python files
- Archive files (``.zip``, ``.tar.gz``, etc.) containing Python files
- JSON files (``.json``) that have Python code embedded in them
- CSV files (``.csv``) that contain Python code

Pedal can also work with ProgSnap data dumps, containing code snapshots:
- Zip files (``.zip``)
- CSV files (``.csv``)
- Sqlite files (``.db``) - this is often the fastest file format!

By far, the simplest option is just Python files or folders containing Python files.
However, the other formats can be useful for more complex scenarios with additional metadata.

Pedal Job Files (``.pedal``) can be used to store the configuration for a Pedal job.

Command Line Parameters
-----------------------

The CLI is invoked with the ``pedal`` command. It accepts the following parameters:


.. argparse::
    :module: pedal.command_line.command_line
    :func: build_parser
    :prog: pedal
