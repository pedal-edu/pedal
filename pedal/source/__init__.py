"""
A Tool for verifying source code, chunking up source code into multiple parts, and substituting code within
the submission.

- Requires: None
- Optional: None
- Category: Syntax

Code Substitution may seem esoteric, but its what powers the code chunking. The submission is literally
modified such that the current submission is replaced by the current file.

"""

from pedal.source.constants import TOOL_NAME_SOURCE
from pedal.source.sections import *
from pedal.source.source import set_source, set_source_file, get_program


__all__ = ['TOOL_NAME_SOURCE',
           'set_source', 'set_source_file', 'get_program',
           'check_section_exists', 'next_section', 'verify_section',
           ]
