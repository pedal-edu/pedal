from pedal.core.report import MAIN_REPORT
from pedal.questions import _setup_questions, _name_hash
from pedal.questions.questions import show_question


class Pool:
    _POOL_TRACKER = 0

    def __init__(self, name, choices, seed=None, report=MAIN_REPORT, position=None):
        self.name = name
        self.choices = choices
        self.seed = seed
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
                if isinstance(force, str):
                    force = _name_hash(force + self.name)
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


def check_pool_exam(name, questions, force=None, seed=None, report=MAIN_REPORT):
    _setup_questions(report)
    # Choose a question
    if force is None:
        if seed is None:
            force = MAIN_REPORT['questions']['seed']
            if isinstance(force, str):
                force = _name_hash(force + name)
        else:
            force = seed
    elif isinstance(force, str):
        force = _name_hash(force + name)
    question = questions[force % len(questions)]
    # Ask it
    show_question(question['instructions'])
    # Check if they're done
    if 'settings' not in question:
        question['settings'] = {}
    question['settings'][SETTING_SHOW_CASE_DETAILS] = False
    results = list(load_question(question))
    if results:
        message, label = results[0]
        gently(message, label=label)