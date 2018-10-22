'''
Some kind of function to break up the sections
'''
import re
from html.parser import HTMLParser

from pedal.report import MAIN_REPORT, Feedback
from pedal import source
from pedal.resolvers import simple

class VPLStyler(HTMLParser):
    HEADERS = ("h1", "h2", "h3", "h4", "h5")
    #TRAILING_NEWLINE_PATTERN = re.compile('[ \t]*\n[ \t]*$', re.MULTILINE)
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.inside_pre = False
    def convert(self, html):
        self.feed(html)
        return self.get_data()
    @property
    def text(self):
        return ''.join(self.fed)
    def get_data(self):
        return self.text
    def force_new_line(self):
        if self.text and self.text[-1] not in ("\n", "\r"):
            self.fed.append("\n")
    def handle_starttag(self, tag, attrs):
        if tag in self.HEADERS:
            self.force_new_line()
            self.fed.append("-")
        elif tag in ("pre",):
            self.force_new_line()
            self.fed.append(">")
            self.inside_pre = True
    def handle_data(self, data):
        if self.inside_pre:
            # Need to prepend ">" to the start of new lines.
            self.fed.append(data.replace("\n", "\n>"))
        else:
            self.fed.append(data)
    def handle_endtag(self, tag):
        if tag in self.HEADERS:
            self.fed.append("")
        elif tag in ("pre", ):
            self.fed.append("")
            self.inside_pre = False

def strip_tags(html):
    return VPLStyler().convert(html)

def find_file(filename, sections=False, report=None):
    if report is None:
        report = MAIN_REPORT
    with open(filename, 'r') as student_file:
        source.set_source(student_file.read(), filename=filename,
                          sections=sections, report=report)

def set_maximum_score(number, cap=True, report=None):
    if report is None:
        report = MAIN_REPORT
    report['vpl']['score_maximum'] = number
    report['vpl']['score_cap'] = cap

def resolve(report=None):
    if report is None:
        report = MAIN_REPORT
    print("<|-")
    (final_success, final_score, final_category, 
     final_label, final_message, final_data,
     final_hide_correctness) = simple.resolve(report)
    print(strip_tags(final_message))
    print("-|>")
    print("Grade :=>>", final_score * report['vpl'].get('score_maximum', 1))
