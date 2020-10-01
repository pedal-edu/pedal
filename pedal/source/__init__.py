"""
A Tool for verifying source code, chunking up source code into multiple parts, and substituting code within
the submission.

- Requires: None
- Optional: None
- Category: Syntax

Code Substitution may seem esoteric, but its what powers the code chunking. The submission is literally
modified such that the current submission is replaced by the current file.

"""

from pedal.source.constants import TOOL_NAME
from pedal.source.sections import (separate_into_sections, check_section_exists,
                                   stop_sections, next_section)
from pedal.source.source import (verify, verify_section, set_source, set_source_file, get_program)


__all__ = ['TOOL_NAME',
           'set_source', 'verify', 'set_source_file', 'get_program',
           'separate_into_sections',
           'check_section_exists', 'next_section', 'verify_section',
           ]
