"""
Check utilities.sorting
"""
import sys
import os
import unittest
from pedal.utilities.progsnap import SqlProgSnap2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

class TestProgsnap(unittest.TestCase):
    def test_progsnap_sort(self):
        progsnap = SqlProgSnap2(here+"datafiles/progsnap2_3.db")
        link_filters = {
            'Subject': {
                'X-IsStaff': "False",
            },
            'Assignment': {
                'X-Name': "Fun%"
            },
        }
        link_selections = {
                'Subject': {
                    'X-Email': 'student_email',
                    'X-Name.First': 'student_first',
                    'X-Name.Last': 'student_last',
                },
                'Assignment': {
                    'X-Name': 'assignment_name',
                    'X-URL': 'assignment_url',
                    'X-Code.OnRun': 'on_run'
                }
            }
        fun_student_edits = progsnap.get_events(
            event_filter={'EventType': 'File.Edit'},
            link_filters=link_filters,
            link_selections=link_selections
        )
        self.assertEqual(212, len(fun_student_edits))
        self.assertIsInstance(fun_student_edits[0], dict)
        self.assertEqual("592", fun_student_edits[0]['event_id'])


if __name__ == '__main__':
    unittest.main(buffer=False)
