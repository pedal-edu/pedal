'''
Some kind of function to break up the sections
'''
import re
from html.parser import HTMLParser

from pedal.report import MAIN_REPORT, Feedback
from pedal.resolvers import simple

class VPLStyler(HTMLParser):
    HEADERS = ("h1", "h2", "h3", "h4", "h5")
    #TRAILING_NEWLINE_PATTERN = re.compile('[ \t]*\n[ \t]*$', re.MULTILINE)
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def convert(self, html):
        self.feed(html)
        return self.get_data()
    def handle_data(self, data):
        self.fed.append(data)
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
    def handle_endtag(self, tag):
        if tag in self.HEADERS:
            self.fed.append("")
        elif tag in ("pre", ):
            self.fed.append("")

def strip_tags(html):
    return VPLStyler().convert(html)

def find_file(filename, pattern='##### (.+)$', report=None):
    if report is None:
        report = MAIN_REPORT
    with open(filename, 'r') as student_file:
        report['vpl']['contents'] = student_file.read()

def set_maximum_score(number, cap=True, report=None):
    if report is None:
        report = MAIN_REPORT
    report['vpl']['score']['maximum'] = number
    report['vpl']['score']['cap'] = cap

def resolve(report=None):
    if report is None:
        report = MAIN_REPORT
    print("< | -")
    simple.resolve(report)
    print("- | >")
    print("Grade :=>>")