Pedal
=====

.. image:: https://github.com/pedal-edu/pedal/workflows/Test%20and%20Lint/badge.svg
    :alt: Unit Tests for 3.6, 3.7, 3.8, 3.9


.. image:: https://github.com/pedal-edu/pedal/workflows/Build%20Documentation/badge.svg
    :alt: Documentation

A collection of tools to analyze student's work in a pipeline.
Pedal not only provides some of these tools, but it provides a *framework*
around those tools.

Installation
============

Install from PyPi::
    
    pip install pedal

Or install from the https://github.com/acbart/pedal repository

Important Concepts
==================

Pedal revolves around providing *Feedback Functions* that can be called in an
Instructor Control Script to generate *Feedback* for a *Submission*, which are
all attached to a *Report*. A *Resolver* can then transform that Feedback into
something that an *Environment* can hand off to a learner (or other interested
party). These Feedback Functions are organized into *Tools*.

.. image:: docsrc/_static/pedal-overview-v3.png

One of our major goals is to attach metadata to feedback to enable easier
analysis, versioning, and evaluation. Although Instructor Control Scripts can
be written very imperatively to specify very complex (or simple) grading logic,
we are trying to reach an elegant, declarative style. This will enable tooling
to automatically generate reports on occurrences of feedback, connect to
datasets like those in the ProgSnap format, and allow us to "unit test our
unit tests".

One of our other goals for this project is to categorize Feedbacks' Conditions
and Responses, using concepts established by Narciss 2006. For example, we
say some Kinds of Responses are "hints" instead of "mistakes". We also say
that Conditions can be Categorized as being from "Specifications" or
"Runtime".

For more information, check out the docs for Pedal_.

.. _Pedal: https://pedal-edu.github.io/pedal
