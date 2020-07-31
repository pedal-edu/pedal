

class Formatter:
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
        return self.html_pre(self.html_code(code), "pedal-python-code")

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
            length_difference = max(len(columns)-len(row)+1, 0)
            colspan = " colspan={length_difference}" if length_difference>1 else ""
            # Make the cells, but we'll treat the last one as special
            for cell in row[:-1]:
                row_text.append(f"    <td{cell_class}>{cell}</td>")
            #  Add in the colspan to the last one
            row_text.append(f"    <td{colspan}{cell_class}>{row[-1]}</td>")
            row_text = "\n".join(row_text)
            body.append(f"  <tr{row_class}>\n{row_text}\n  </tr>")
        body = "\n".join(body)
        return (f"<table{table_class}>"
                f"   <tr{header_class}>\n{header}\n  </tr>"
                f"   {body}"
                f"</table>")
