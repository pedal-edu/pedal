from pedal.plugins.vpl_unittest import UnitTestedAssignment

"""
Some kind of function to break up the sections
"""
import re
import sys
from html.parser import HTMLParser

from pedal.report import MAIN_REPORT
from pedal import source
from pedal.resolvers import sectional
from pedal.cait.cait_api import expire_cait_cache


class VPLStyler(HTMLParser):
    HEADERS = ("h1", "h2", "h3", "h4", "h5")

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
        elif tag in ("pre",):
            self.fed.append("")
            self.inside_pre = False


def strip_tags(html):
    return VPLStyler().convert(html)


def find_file(filename, sections=False, independent=False, report=None):
    if report is None:
        report = MAIN_REPORT
    try:
        with open(filename, 'r') as student_file:
            source.set_source(student_file.read(), filename=filename,
                              sections=sections, independent=independent,
                              report=report)
    except IOError:
        message = ("The given filename ('{filename}') was either not found"
                   " or could not be opened. Please make sure the file is"
                   " available.").format(filename=filename)
        report.attach('Source File Not Found', category='Syntax', tool='VPL',
                      group=0 if sections else None,
                      mistake={'message': message})
        report['source']['success'] = False


def set_maximum_score(number, cap=True, report=None):
    if report is None:
        report = MAIN_REPORT
    report['vpl']['score_maximum'] = number
    report['vpl']['score_cap'] = cap


def resolve(report=None, custom_success_message=None):
    if report is None:
        report = MAIN_REPORT
    print("<|--")
    success, score, hc, messages_by_group = sectional.resolve(report)
    last_group = 0
    for group, messages in sorted(messages_by_group.items()):
        if group != last_group:
            for intermediate_section in range(last_group, group, 2):
                print("-" + report['source']['sections'][1 + intermediate_section])
        printed_first_bad = False
        for message in messages:
            if message['priority'] == 'positive':
                print(strip_tags(message['message']))
            elif not printed_first_bad:
                print(strip_tags(message['message']))
                printed_first_bad = True
        last_group = group
    print("-Overall")
    if success:
        if custom_success_message is None:
            print("Complete! Great job!")
        else:
            print(custom_success_message)
    else:
        print("Incomplete")
    print("--|>")
    print("Grade :=>>", round(score))


class SectionalAssignment:
    max_points = 1
    sections = None

    def __init__(self, filename=None, max_points=None, report=None):
        self.report = MAIN_REPORT if report is None else report
        find_file(filename if filename else self.filename,
                  sections=True, report=report)
        set_maximum_score(self.max_points
                          if max_points is None else max_points)
        source.check_section_exists(self.sections)

    def pre_test(self):
        source.next_section()
        verified = source.verify_section()
        expire_cait_cache()
        return verified

    def post_test(self):
        return True

    def resolve(self):
        checks = ((self.pre_test() and
                   getattr(self, attr)() and
                   self.post_test())
                  for attr in dir(self)
                  if attr.startswith('test_') and
                  callable(getattr(self, attr)))
        if all(checks):
            self.report.set_success()
        resolve(report=self.report)


from pedal.plugins.vpl_unittest import UnitTestedAssignment


def unittest_resolver(phases, report=None, custom_success_message=None):
    success = True
    for title, phase in phases:
        outcome = phase()._run_all_tests()
        if not outcome:
            break
        success = success and outcome
    resolve(custom_success_message=custom_success_message)
