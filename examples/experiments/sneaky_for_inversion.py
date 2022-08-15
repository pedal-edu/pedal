student_code = """
counter = 0
for _time in _main.do_step():
    counter += 1
    second_counter = True
    print(counter)
"""


def grade_loop_iteration(student):
    print("STARTING", 'second_counter' in student)
    print("FIRST YIELD")
    yield
    print("I AM BACK.")
    print("SECOND YIELD")
    yield
    print("I AM BACK", 'second_counter' in student)


class MainFunction:
    def __init__(self, step, data):
        self.step = step
        self.data = data
        self.time = 0

    def do_step(self):
        print(globals())
        self.time += 1
        yield from self.step(self.data)


def run_async(student_code, callback):
    c = compile(student_code, 'answer.py', 'exec')
    t = 0
    d = {}
    d['_main'] = MainFunction(callback, d)
    exec(c, d)
    return d


print('counter' in run_async(student_code, grade_loop_iteration))