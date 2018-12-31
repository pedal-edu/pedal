'''
exercise_id: 267
title: #42.1) Nested Dictionaries
topics:  Nested Structures
prerequisites:
instructions:-----
<p>Given the following dictionary representing this course, print out the first instructor and the title of the Day 2 assignment using dictionary lookups and list indexing. Make sure to print out each of these on separate lines.<br></p>
-----
[systems]
language: Python
version: >= 3.3
start:-----
course = {
    "Instructors": ["Klaus", "Wrex"],
    "ID": {
        "Department": "CS",
        "Number": 1064
    },
    "Name": "Introduction to Python",
    "Assignments": {
        "Day 1": {
            "Points": 10,
            "Title": "Introduction"
        },
        "Day 2":{
            "Points": 5,
            "Title": "Installing Python"
        },
    }
}
-----
on_run:-----
'''

from pedal import *

ast = parse_program()

original_course = {
    "Instructors": ["Klaus", "Wrex"],
    "ID": {
        "Department": "CS",
        "Number": 1064
    },
    "Name": "Introduction to Python",
    "Assignments": {
        "Day 1": {
            "Points": 10,
            "Title": "Introduction"
        },
        "Day 2":{
            "Points": 5,
            "Title": "Installing Python"
        },
    }
}

str_values = [s.s for s in ast.find_all('Str')]
no_forbidden_values = True
for literal in ["Klaus", "Wrex", "Introduction to Python", "Introduction", "Installing Python"]:
    if str_values.count(literal) > 1:
        explain('The string <code>{}</code> should only appear in your program once, when the original variable <code>course</code> is defined. Think about how to access a dictionary value using a look up.'.format(repr(literal)))
        no_forbidden_values = False
if no_forbidden_values:
    num_values = [n.n for n in ast.find_all("Num")]
    has_needed_values = True
    if str_values.count("Instructors") < 2:
        explain('The key <code>{}</code> should be used.'.format(repr('Instructors')))
    elif 0 not in num_values:
        gently("You will need to index the first element of a list.")
    else:
        for literal in ["Assignments", "Day 2", "Title"]:
            if str_values.count(literal) < 2:
                explain('The key <code>{}</code> should be used.'.format(repr(literal)))
                has_needed_values = False
        if has_needed_values:
            if len(get_output()) < 2:
                gently("You are not printing two answers.")
            elif len(get_output()) > 2:
                gently("You are printing too many things.")
            elif "Klaus" not in get_output():
                gently("You not printed out the first instructor.")
            elif "Installing Python" not in get_output():
                gently("You have not printed out the Title of the Assignment on Day 2.")
            elif len(ast.find_all("Subscript")) < 5:
                gently("You will need to do more dictionary lookups and list indexing.")
            elif 'course' not in student.data:
                explain("Do not remove the <code>course</code> variable.")
            elif student.data['course'] != original_course:
                explain("Do not change the <code>course</code> variable.")
            else:
                set_success()
-----