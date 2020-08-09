"""
Runs pedal as a toplevel module
"""
import sys

from pedal.command_line.command_line import parse_args, main

args = parse_args()
main(args)
