

class Formatter:
    def html_pre(self, text, classes=None):
        if classes is None:
            return f"<pre>{text}</pre>"
        else:
            return f"<pre class='{classes}'>{text}</pre>"

    def html_div(self, contents, classes=None):
        if classes is None:
            return f"<div>{contents}</div>"
        else:
            return f"<div class='{classes}'>{contents}</div>"

    def html_code(self, contents, classes=None):
        if classes is None:
            return f"<div>{contents}</div>"
        else:
            return f"<div class='{classes}'>{contents}</div>"

    ############################################################################

    def python_code(self, code):
        return self.html_pre(self.html_code(code), "pedal-python-code")

    def python_value(self, code):
        return self.html_pre(code, "pedal-python-value")

    def inputs(self, inputs):
        return self.html_pre(inputs, "pedal-inputs")

    def output(self, output):
        return self.html_pre(output, "pedal-output")

    def traceback(self, traceback):
        return self.html_div(traceback, "pedal-traceback")

    def name(self, name):
        return self.html_code(name, "pedal-name")

    def line(self, line_number):
        return str(line_number)
