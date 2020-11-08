"""
Tests for checking that the plotting extension works.
"""
from textwrap import dedent

from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE
from pedal.extensions.plotting import *


code_hist_and_plot = ('''
import matplotlib.pyplot as plt
plt.hist([1,2,3])
plt.title("My line plot")
plt.show()
plt.plot([4,5,6])
plt.show()''')[1:]


class TestPlots(ExecutionTestCase):

    def test_check_for_plot_correct_hist(self):
        with Execution(code_hist_and_plot) as e:
            self.assertEqual(assert_plot('hist', [1, 2, 3]), False)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_check_for_plot_wrong_hist(self):
        with Execution(code_hist_and_plot) as e:
            assert_plot('hist', [1, 2, 3, 4])
        self.assertFeedback(e, "Plot Data Incorrect\n"
                               "You have created a histogram, but it does not "
                               "have the right data.")

    def test_check_for_plot_correct_plot(self):
        with Execution(code_hist_and_plot) as e:
            self.assertEqual(assert_plot('line', [4, 5, 6]), False)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_check_for_plot_wrong_plot(self):
        with Execution(code_hist_and_plot) as e:
            assert_plot('line', [4, 5, 6, 7])
        self.assertFeedback(e, "Plot Data Incorrect\n"
                               "You have created a line plot, but it does not "
                               "have the right data.")

    def test_assert_plot_wrong_type_of_plot(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("My line plot")
            plt.show()
        ''')
        with Execution(student_code) as e:
            assert_plot('hist', [1, 2, 3])
        self.assertFeedback(e, "Wrong Plot Type\n"
                               "You have plotted the right data, but you appear "
                                "to have not plotted it as a histogram.")

    def test_assert_plot_wrong_data_place(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("Wrong graph with the right data")
            plt.show()
            plt.hist([4,5,6])
            plt.title("Right graph with the wrong data")
            plt.show()
        ''')
        with Execution(student_code) as e:
            assert_plot('hist', [1, 2, 3])
        self.assertFeedback(e, "Plotting Another Graph\n"
                               "You have created a histogram, but it does not "
                               "have the right data. That data appears to have "
                               "been plotted in another graph.")

    def test_assert_plot_missing_plot_and_data(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("My line plot")
            plt.show()
        ''')
        with Execution(student_code) as e:
            assert_plot('hist', [4, 5, 6])
        self.assertFeedback(e, "Missing Plot\n"
                               "You have not created a histogram with the proper data.")

    def test_assert_plot_empty_scatter(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.scatter([], [])
            plt.title("Nothingness and despair")
            plt.show()
        ''')
        with Execution(student_code) as e:
            assert_plot('scatter', [])
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_plot_simple_scatter(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.scatter([1,2,3], [4,5,6])
            plt.title("Some actual stuff")
            plt.show()
        ''')
        with Execution(student_code) as e:
            assert_plot('scatter', [[1, 2, 3], [4, 5, 6]])
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_incorrect_plt(self):
        student_code = dedent('''
            import matplotlib.pyplot
            plt.scatter([1,2,3], [4,5,6])
            plt.title("Some actual stuff")
            plt.show()
        ''')
        with Execution(student_code) as e:
            self.assertTrue(prevent_incorrect_plt())
        self.assertFeedback(e, "Wrong MatPlotLib Import\n"
                               "You have imported the plt module, but"
                               " you did not rename it to "
                               "matplotlib.pyplot"
                               " using import matplotlib.pyplot as plt.")

    def test_prevent_incorrect_plt_missing_plt(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            scatter([1,2,3], [4,5,6])
            plt.title("Some actual stuff")
            plt.show()
        ''')
        with Execution(student_code) as e:
            self.assertTrue(prevent_incorrect_plt())
        self.assertFeedback(e, "Missing MatPlotLib Import\n"
                               "You have attempted to use the MatPlotLib "
                               "function named plt.scatter. "
                               "However, you imported MatPlotLib in a way that "
                               "does not allow you to use the function "
                               "directly. I recommend you use "
                               "scatter instead, after you use "
                               "import matplotlib.pyplot as plt.")

    def test_prevent_incorrect_plt_success(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.scatter([1,2,3], [4,5,6])
            plt.title("Some actual stuff")
            plt.show()
        ''')
        with Execution(student_code) as e:
            self.assertFalse(prevent_incorrect_plt())
