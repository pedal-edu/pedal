"""
Utilities and classes related to formatting a Feedback Message.
"""


def chomp_spec(format_spec, word):
    """ Return a new version of format_spec without the ``word`` and
    (if there are multiple format_spec given) the extra colon. """
    if format_spec.endswith(word):
        format_spec = format_spec[:-len(word)]
        if format_spec and format_spec[-1] == ':':
            format_spec = format_spec[:-1]
    return format_spec


class FeedbackFieldWrapper:
    """
    Wraps an individual field within a Feedback message.

    Args:
        key (str): The name of the field.
        value (Any): The value to interpolate into the message.
        formatter (Formatter): The formatter to use from the report.
    """
    def __init__(self, key, value, formatter):
        self.key = key
        self.value = value
        self.formatter = formatter

    def __getattr__(self, key):
        return FeedbackFieldWrapper(self.key, getattr(self.value, key), self.formatter)

    def __getitem__(self, index):
        return FeedbackFieldWrapper(self.key, self.value[index], self.formatter)

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def __format__(self, format_spec):
        value = str(self.value)
        for formatter_name in self.formatter.available:
            if format_spec.endswith(formatter_name):
                format_spec = chomp_spec(format_spec, formatter_name)
                value = getattr(self.formatter, formatter_name)(self.value)
                break
        return value.__format__(format_spec)

# TODO: Convert Formatter into HtmlFormatter, and then make Formatter text by
#       default.


class Formatter:
    """ Utility class for wrapping a feedback message with HTML or other
            extra information. Can be subclassed by a different environment and
            attached to a Report, in order to change how we create feedback. """

    available = ['exception', 'filename', 'frame', 'traceback',
                 # 'html_code', 'html_div', 'html_pre', 'html_span', 'html_tag',
                 'inputs', 'line', 'name', 'output',
                 'python_code', 'python_expression', 'python_value',
                 'table']

    def __init__(self, report=None):
        """ Can optionally specify a report, in order to look over current
        feedback and settings. """
        self.report = report

    def update_report(self, report):
        """ Change the currently set report for this formatter. """
        self.report = report

    def pre(self, text):
        return "\n".join(["    " + line for line in text.split("\n")])

    def python_code(self, code):
        return self.pre(code)

    def python_expression(self, code):
        return str(code)

    def filename(self, filename):
        return filename

    def python_value(self, code):
        return self.pre(code)

    def inputs(self, inputs):
        return self.pre(inputs)

    def output(self, output):
        return self.pre(output)

    def traceback(self, traceback):
        return traceback

    def name(self, name):
        return name

    def line(self, line_number):
        return line_number

    def frame(self, name):
        return name

    def exception(self, exception):
        return self.pre(exception)

    def table(self, rows, columns):
        result = []
        result.append(" | ".join(columns))
        for row in rows:
            result.append(" | ".join(row))
        return "\n" + ("\n".join(result))

    def check_mark(self):
        return " "

    def negative_mark(self):
        return "×"


class HtmlFormatter(Formatter):

    def html_tag(self, tag, contents, classes=None):
        if classes is None:
            return f"<{tag}>{contents}</{tag}>"
        else:
            return f"<{tag} class='{classes}'>{contents}</{tag}>"

    def html_pre(self, text, classes=None):
        return self.html_tag('pre', text, classes)

    def html_div(self, contents, classes=None):
        return self.html_tag('div', contents, classes)

    def html_code(self, contents, classes=None):
        return self.html_tag('code', contents, classes)

    def html_span(self, contents, classes=None):
        return self.html_tag('span', contents, classes)

    ############################################################################

    def python_code(self, code):
        return self.html_pre(self.html_code(code), "pedal-python-code python")

    def python_expression(self, code):
        return self.html_code(code)

    def filename(self, filename):
        return self.html_code(filename, "pedal-filename")

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

    def frame(self, name):
        return self.html_code(name, "pedal-frame")

    def exception(self, exception):
        return self.html_pre(exception, "pedal-exception")

    def table(self, rows, columns):
        """
        Creates a tabular representation of the rows and columns.
        If a row's length is less than the columns' length, then it will
        receive a colspan to stretch its last cell to fit the table.

        Args:
            rows (list[list[str]]): The 2D cells of the table.
            columns (list[str]): The header rows

        Returns:
            str: The completed table.
        """
        cell_class = " class='pedal-cell'"
        row_class = " class='pedal-row'"
        table_class = " class='pedal-table'"
        header_class = " class='pedal-header'"
        header = "\n".join(f"    <th{cell_class}>{column}</th>" for column in columns)
        body = []
        for row in rows:
            # Skip empty rows
            if not row:
                continue
            row_text = []
            # If we miss some columns, expand the last one.
            length_difference = max(len(columns) - len(row) + 1, 0)
            colspan = " colspan={length_difference}" if length_difference > 1 else ""
            # Make the cells, but we'll treat the last one as special
            for cell in row[:-1]:
                row_text.append(f"    <td{cell_class}>{cell}</td>")
            #  Add in the colspan to the last one
            row_text.append(f"    <td{colspan}{cell_class}>{row[-1]}</td>")
            row_text = "\n".join(row_text)
            body.append(f"  <tr{row_class}>\n{row_text}\n  </tr>")
        body = "\n".join(body)
        return (f"\n<table{table_class}>"
                f"   <tr{header_class}>\n{header}\n  </tr>"
                f"   {body}"
                f"</table>")

    def check_mark(self):
        return self.html_span("&#10004;", "pedal-positive-mark")

    def negative_mark(self):
        return self.html_span("&#10060;", "pedal-negative-mark")


class TextFormatter(Formatter):
    pass
