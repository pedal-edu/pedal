"""
A Tool for verifying source code, and chunking up source code into multiple parts.

- Requires: None
- Optional: None
- Category: Syntax


"""

from pedal.source.constants import TOOL_NAME_SOURCE
from pedal.source.sections import *
from pedal.source.source import set_source, set_source_file, get_program


__all__ = ['TOOL_NAME_SOURCE',
           'set_source', 'set_source_file', 'get_program',
           'check_section_exists', 'next_section', 'verify_section',
           ]
