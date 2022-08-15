student_code = """
counter = 0
def _main_step():
    global counter
    counter += 1
    second_counter = True
    show(counter)
"""


class AsyncRun:
    def __init__(self, data):
        self.time = 0
        self.data = data
        self.shown = []
        self.data['show'] = self.show

    def show(self, *args, **kwargs):
        self.shown.append((args, kwargs))

    def step(self):
        self.time += 1
        self.data['_main_step']()


def run_async():
    c = compile(student_code, 'answer.py', 'exec')
    t = 0
    d = {}
    runner = AsyncRun(d)
    exec(c, d)
    return runner


execution = run_async()
print("Initial setup finished")
assert execution.data['counter'] == 0
execution.step()
print("First check")
assert execution.data['counter'] == 1
execution.step()
print("Second check")
print(execution.shown)
