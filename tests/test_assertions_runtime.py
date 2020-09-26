"""
Tests for checking that runtime assertions are working as expected.
"""
from pedal.assertions.feedbacks import assert_group
from pedal.assertions.runtime import *
from pedal.sandbox.commands import call, start_trace, get_sandbox, evaluate
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE
import unittest


class TestAssertions(ExecutionTestCase):

    def test_assert_equal_basic_passes(self):
        with Execution('5') as e:
            assert_equal(5, 5)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_equal_basic_fails(self):
        with Execution('5') as e:
            assert_equal(5, 4)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
<pre class='pedal-output'>5 != 4</pre>""")

    def test_assert_equal_missing_function(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            assert_equal(e.student.call('minus', 1, 2), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
The following exception occurred:
<pre class='pedal-output'>The function minus does not exist.</pre>""")

    def test_assert_equal_call_left_fails(self):
        with Execution('def add(a, b): return a-b', run_tifa=False) as e:
            assert_equal(e.student.call('add', 1, 2), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>add(1, 2)</code></pre>
The value of the result was:
<pre class='pedal-python-value'>-1</pre>
But I expected the result to be equal to:
<pre class='pedal-python-value'>3</pre>""")

    def test_assert_equal_call_left_passes(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            assert_equal(e.student.call('add', 1, 2), 3)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_equal_call_right_fails(self):
        with Execution('def add(a, b): return a-b', run_tifa=False) as e:
            assert_equal(3, e.student.call('add', 1, 2))
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>add(1, 2)</code></pre>
The value of the result was:
<pre class='pedal-python-value'>-1</pre>
But I expected the result to be equal to:
<pre class='pedal-python-value'>3</pre>""")

    def test_assert_equal_call_right_passes(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            assert_equal(3, e.student.call('add', 1, 2))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_in_call_left_fails(self):
        with Execution('def make_int(): return 7', run_tifa=False) as e:
            assert_in(e.student.call('make_int'), [1, 2, 3])
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>make_int()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>7</pre>
But I expected the result to be in:
<pre class='pedal-python-value'>[1, 2, 3]</pre>""")

    def test_assert_in_call_right_fails(self):
        with Execution('def make_ints(): return [1,2,3]', run_tifa=False) as e:
            assert_in(10, e.student.call('make_ints'))
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>make_ints()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>[1, 2, 3]</pre>
But I expected the result to contain:
<pre class='pedal-python-value'>10</pre>""")

    def test_assert_is_none_call_left_fails(self):
        with Execution('def do_math(): return 1+2', run_tifa=False) as e:
            assert_is_none(e.student.call('do_math'))
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>do_math()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>3</pre>
But I expected the result to be None""")

    def test_assert_is_none_call_left_passes(self):
        with Execution('def do_math(): 1+2', run_tifa=False) as e:
            assert_is_none(e.student.call('do_math'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_is_call_left_passes(self):
        with Execution('r = [1, 2]\ndef get_list(): return r', run_tifa=False) as e:
            result_list = e.student.call('get_list')
            value_list = e.student.data['r']
            assert_is(result_list, value_list)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_is_basic_passes(self):
        with Execution('0 is 0', run_tifa=False) as e:
            l = [1,2,3]
            r = l
            assert_is(l, r)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_is_call_left_fails(self):
        with Execution('r = [1, 2]\ndef get_list(): return r', run_tifa=False) as e:
            result_list = e.student.call('get_list')
            assert_is(result_list, [1, 2])
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>get_list()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>[1, 2]</pre>
But I expected the result to be identical to:
<pre class='pedal-python-value'>[1, 2]</pre>""")

    def test_assert_length_equal_basic_passes(self):
        with Execution('5') as e:
            assert_length_equal([1,2,3], 3)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_length_equal_basic_fails(self):
        with Execution('5') as e:
            assert_length_equal([1, 2, 3], 4)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
<pre class='pedal-output'>[1, 2, 3] did not have the length 4</pre>""")

    def test_assert_length_equal_call_left_fails(self):
        with Execution('def get(a, b): return [a,b]', run_tifa=False) as e:
            assert_length_equal(e.student.call('get', 1, 2), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>get(1, 2)</code></pre>
The value of the result was:
<pre class='pedal-python-value'>[1, 2]</pre>
But I expected the result to have the length:
<pre class='pedal-python-value'>3</pre>""")

    def test_assert_length_equal_call_left_passes(self):
        with Execution('def get(a, b): return "test"', run_tifa=False) as e:
            assert_length_equal(e.student.call('get', 1, 2), 4)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_length_equal_call_right_fails(self):
        with Execution('def get(): return 5', run_tifa=False) as e:
            assert_length_equal([1,2,3], e.student.call('get'))
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>get()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>5</pre>
But I expected the result to be the length of:
<pre class='pedal-python-value'>[1, 2, 3]</pre>""")

    def test_assert_length_equal_call_right_passes(self):
        with Execution('def get(): return 3', run_tifa=False) as e:
            assert_length_equal([1, 2, 3], e.student.call('get'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_contains_subset_call_left_passes(self):
        with Execution('def get(): return [1,2,3]', run_tifa=False) as e:
            assert_contains_subset(e.student.call('get'), [1, 2, 3, 4, 5])
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_contains_subset_call_left_fails(self):
        with Execution('def get(): return [1,2,3]', run_tifa=False) as e:
            assert_contains_subset(e.student.call('get'), [1,2])
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>get()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>[1, 2, 3]</pre>
But I expected the result to be in:
<pre class='pedal-python-value'>[1, 2]</pre>""")

    def test_assert_not_contains_subset_call_left_passes(self):
        with Execution('def get(): return [1,2,3,4,5]', run_tifa=False) as e:
            assert_not_contains_subset(e.student.call('get'), [1, 2, 3])
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_not_contains_subset_call_left_fails(self):
        with Execution('def get(): return [1,2]', run_tifa=False) as e:
            assert_not_contains_subset(e.student.call('get'), [1, 2, 3])
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>get()</code></pre>
The value of the result was:
<pre class='pedal-python-value'>[1, 2]</pre>
But I expected the result to not be in:
<pre class='pedal-python-value'>[1, 2, 3]</pre>""")

    def test_assert_output_call_left_passes(self):
        with Execution('def hi(): print("Hello world!")', run_tifa=False) as e:
            assert_output(e.student.call('hi'), "Hello world!")
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_output_call_left_fails(self):
        with Execution('def hi(): print("Hello world!")', run_tifa=False) as e:
            assert_output(e.student.call('hi'), "Oh Hi There")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>hi()</code></pre>
The function printed:
<pre class='pedal-output'>Hello world!</pre>
But I expected the output to be:
<pre class='pedal-output'>Oh Hi There</pre>""")

    def test_assert_has_function_passes(self):
        with Execution('def hi(): print("Hello world!")', run_tifa=False) as e:
            assert_has_function(e.student, "hi")
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_data_variable_fails(self):
        with Execution('alpha = 4', run_tifa=False) as e:
            assert_equal(e.student['alpha'], 5)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran your code.
The value of <code class='pedal-name'>alpha</code> was:
<pre class='pedal-python-value'>4</pre>
But I expected <code class='pedal-name'>alpha</code> to be equal to:
<pre class='pedal-python-value'>5</pre>""")

    def test_assert_group_fails_some_errors(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            with assert_group('add') as g:
                assert_equal(e.student.call('add', 1, 2), 3)
                assert_equal(e.student.call('add', 1, 4), 6)
                assert_equal(e.student.call('add', 1, "2"), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor tests.
You passed 1/3 tests.

I ran your function <code class='pedal-name'>add</code> on some new arguments.
<table class='pedal-table'>   <tr class='pedal-header'>
    <th class='pedal-cell'></th>
    <th class='pedal-cell'>Arguments</th>
    <th class='pedal-cell'>Returned</th>
    <th class='pedal-cell'>Expected</th>
  </tr>     <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-positive-mark'>&#10004;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, 2</code></pre></td>
    <td class='pedal-cell'>3</td>
    <td class='pedal-cell'>3</td>
  </tr>
  <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-negative-mark'>&#10060;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, 4</code></pre></td>
    <td class='pedal-cell'>5</td>
    <td class='pedal-cell'>6</td>
  </tr>
  <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-negative-mark'>&#10060;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, '2'</code></pre></td>
    <td class='pedal-cell'>unsupported operand type(s) for +: 'int' and 'str'</td>
    <td class='pedal-cell'>3</td>
  </tr></table>""")

    def test_assert_group_fails_all(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            with assert_group('add') as g:
                assert_equal(e.student.call('add', 1, 3), 3)
                assert_equal(e.student.call('add', 1, 4), 6)
                assert_equal(e.student.call('add', 1, 3), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor tests.
You passed 0/3 tests.

I ran your function <code class='pedal-name'>add</code> on some new arguments.
<table class='pedal-table'>   <tr class='pedal-header'>
    <th class='pedal-cell'></th>
    <th class='pedal-cell'>Arguments</th>
    <th class='pedal-cell'>Returned</th>
    <th class='pedal-cell'>Expected</th>
  </tr>     <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-negative-mark'>&#10060;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, 3</code></pre></td>
    <td class='pedal-cell'>4</td>
    <td class='pedal-cell'>3</td>
  </tr>
  <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-negative-mark'>&#10060;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, 4</code></pre></td>
    <td class='pedal-cell'>5</td>
    <td class='pedal-cell'>6</td>
  </tr>
  <tr class='pedal-row'>
    <td class='pedal-cell'><span class='pedal-negative-mark'>&#10060;</span></td>
    <td class='pedal-cell'><pre class='pedal-python-code python'><code>1, 3</code></pre></td>
    <td class='pedal-cell'>4</td>
    <td class='pedal-cell'>3</td>
  </tr></table>""")

    def test_assert_group_passes(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            with assert_group('add') as g:
                assert_equal(e.student.call('add', 1, 3), 4)
                assert_equal(e.student.call('add', 1, 4), 5)
                assert_equal(e.student.call('add', 1, 3), 4)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_coverage_fails(self):
        with Execution('def add(a, b):\n  return a+b', run_tifa=False, tracer_style='coverage') as e:
            ensure_coverage(.9)
        self.assertFeedback(e, """You Must Test Your Code
Your code coverage is not adequate. You must cover at least 90% of your code to receive feedback. So far, you have only covered 50%.""")

    def test_assert_coverage_passes(self):
        with Execution('def add(a, b):\n  return a+b\nadd(1,2)', run_tifa=False, tracer_style='coverage') as e:
            ensure_coverage()
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_group_passes_but_earlier_fails(self):
        with Execution('def add(a, b): return a+b', run_tifa=False) as e:
            assert_equal(e.student.call('add', 4, 1), 7)
            with assert_group('add') as g:
                assert_equal(e.student.call('add', 1, 3), 4)
                assert_equal(e.student.call('add', 1, 4), 5)
                assert_equal(e.student.call('add', 1, 3), 4)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran the code:
<pre class='pedal-python-code python'><code>add(4, 1)</code></pre>
The value of the result was:
<pre class='pedal-python-value'>5</pre>
But I expected the result to be equal to:
<pre class='pedal-python-value'>7</pre>""")

    def test_assert_equal_variable_passes(self):
        with Execution('x=7\nprint(x)') as e:
            assert_has_variable(e.student, 'x')
            assert_equal(e.student.data['x'], 7)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_equal_variable_fails_does_not_exist(self):
        with Execution('y=7\nprint(y)') as e:
            assert_has_variable(e.student, 'x')
            assert_equal(e.student.data.get('x'), 7)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran your code.
The variable x was not created.""")

    def test_assert_equal_variable_fails_wrong_value(self):
        with Execution('x=3\nprint(x)') as e:
            assert_has_variable(e.student, 'x')
            assert_equal(evaluate('x'), 7)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I evaluated the expression:
<pre class='pedal-python-code python'><code>x</code></pre>
The value of the result was:
<pre class='pedal-python-value'>3</pre>
But I expected the result to be equal to:
<pre class='pedal-python-value'>7</pre>""")


    def test_assert_type_passes_int(self):
        with Execution('x=3\nprint(x)') as e:
            assert_type(evaluate('x'), int)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_type_fails_int(self):
        with Execution('x="3"\nprint(x)') as e:
            assert_type(evaluate('x'), int)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I evaluated the expression:
<pre class='pedal-python-code python'><code>x</code></pre>
The value of the result was:
<pre class='pedal-python-value'>'a string'</pre>
But I expected the result to not be a value of type:
<pre class='pedal-python-value'>'a number'</pre>""")

    def test_assert_chain_passes(self):
        with Execution('x=3\nprint(x)') as e:
            assert_has_variable(e.student, 'x')
            assert_type(evaluate('x'), int)
            assert_equal(evaluate('x'), 3)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_chain_missing_variable(self):
        with Execution('y=3\nprint(y)') as e:
            assert_has_variable(e.student, 'x')
            assert_type(evaluate('x'), int)
            assert_equal(evaluate('x'), 3)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I ran your code.
The variable x was not created.""")

    def test_assert_chain_incompatible_type(self):
        with Execution('x=3\nprint(x)') as e:
            assert_has_variable(e.student, 'x')
            assert_type(evaluate('x'), list)
            assert_equal(evaluate('set(x)'), {})
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
I evaluated the expression:
<pre class='pedal-python-code python'><code>x</code></pre>
The value of the result was:
<pre class='pedal-python-value'>'a number'</pre>
But I expected the result to not be a value of type:
<pre class='pedal-python-value'>'a list'</pre>""")

if __name__ == '__main__':
    unittest.main(buffer=False)
