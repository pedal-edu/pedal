import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from pedal.mistakes.instructor_filter import *


class FilterMistakeTests(MistakeTest):
    pass
