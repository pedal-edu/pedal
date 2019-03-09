from pedal.report.imperative import MAIN_REPORT

import hashlib

def _name_hash(name):
    return hashlib.md5(name.encode('utf8')).digest()[0]

def _setup_questions(report):
    '''
    Initialize any necessary fields for the report's question tool.
    
    Args:
        report (Report): The report object to store data and feedback in.
    '''
    if 'questions' not in report:
        report['questions'] = {
            'seed': 0
        }

def set_seed(seed_value, report=None):
    '''
    Sets the seed that will be used in selecting questions.
    
    Args:
        seed_value (int or str or iterable[int]): The value to use when
            selecting questions, deterministically. If int, the same index
            will be used for all questions. If an iterable of ints, each
            one will serve as the index for the corresponding problem (throws
            an exception if the iterable isn't long enough). If a string,
            it will be hashed to a value (the hash is deterministic across
            platforms) that will be modulo'd to be in the right range for the
            pool. Presently, hashing generates values from [0, 256) so you
            need to limit your questions to 256.
        report (Report): The report object to store data and feedback in. If
            left None, defaults to the global MAIN_REPORT.
    '''
    if report is None:
        report = MAIN_REPORT
    report['questions']['seed'] = seed_value
