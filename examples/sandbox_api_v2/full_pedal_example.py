"""
This file is meant to be an idealized example of Pedal with a completely generic autograding environment that
wants to customize everything without actually changing anything.
"""
from pedal.core.submission import Submission
from pedal.environments.autograder import setup_pedal
from pedal.core.resolver import Resolver

autograder = setup_pedal()
student_submission = Submission(files={'answer.py': 'print("Hello world!")'},
                                user={"name": "Ada Lovelace"},
                                assignment={"name": "#24.3 List Indexing in Functions"},
                                course={"name": "Introduction to Computer Science"})

contextualize_report(student_submission)

from pedal.source import validate
validate()

resolve()