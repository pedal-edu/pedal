"""
A package for analyzing student code.
"""
import sys
import os
import logging

# Setup Logging
logger = logging.getLogger('pedal')
logger.addHandler(logging.NullHandler())
logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'ERROR').upper()
)

logger.debug("Pedal import started")

# Core Features
from pedal.core.report import MAIN_REPORT
from pedal.core.submission import Submission
from pedal.core.commands import *
logger.debug("Pedal core import finished")

# Default Tools
from pedal.source import *
logger.debug("Source Tool import finished")

from pedal.sandbox.commands import *
logger.debug("Sandbox Tool import finished")

from pedal.cait import *
logger.debug("CAIT Tool import finished")

from pedal.assertions.commands import *
logger.debug("Assertions Tool import finished")

# Type System Configuration
from pedal.types.config import (
    configure_type_system, TypeSystemConfig,
    get_default_type_system_config, set_default_type_system_config
)
logger.debug("Type System Configuration import finished")

from pedal.resolvers import *
logger.debug("Resolvers Tool import finished")

# Provide type of `student` data object (setup via Sandbox)
student: Sandbox

logger.debug("Pedal import finished")
