"""
A tool for providing dynamic questions to learners.
"""

NAME = 'Questions'
SHORT_DESCRIPTION = "Provides dynamic questions to learners"
DESCRIPTION = '''
'''
REQUIRES = []
OPTIONALS = []
CATEGORY = 'Instructions'

__all__ = ['NAME', 'DESCRIPTION', 'SHORT_DESCRIPTION', 'REQUIRES', 'OPTIONALS',
           'Question', 'Pool', 'set_seed']

from pedal.report.imperative import MAIN_REPORT
from pedal.questions.setup import _setup_questions, set_seed

class Question:
    def __init__(self, name, instructions, tests, seed=None, report=None):
        self.name = name
        self.instructions = instructions
        self.tests = tests
        self.seed = seed
        if report is None:
            report = MAIN_REPORT
        self.report = report
        self.answered = False
    
    def answer(self):
        self.answered = True
    
    def ask(self):
        for test in self.tests:
            test(self)
        if not self.answered:
            self.report.attach('Question', category='Instructions', tool='Questions',
                               group=self.report.group,
                               priority='instructions',
                               hint=self.instructions)

class Pool:
    _POOL_TRACKER = 0
    def __init__(self, name, choices, seed=None, report=None, position=None):
        self.name = name
        self.choices = choices
        self.seed = seed
        if report is None:
            report = MAIN_REPORT
        self.report = report
        if position is None:
            position = Pool._POOL_TRACKER
            Pool._POOL_TRACKER += 1
        self.position = position

    def choose(self, force=None):
        _setup_questions(self.report)
        if force is None:
            if self.seed is None:
                force = self.report['questions']['seed']
                # Assume iterable; could be check that throws better error
                if not isinstance(force, int):
                    force = force[self.position]
            else:
                force = self.seed
        return self.choices[force % len(self.choices)]
    
    @property
    def answered(self):
        for choice in self.choices:
            if choice.answered:
                return True
        return False
