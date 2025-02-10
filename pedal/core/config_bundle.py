import argparse
from typing import Optional, List, Dict, Any, Type, TypeVar
from pedal.core.report import Report
from pedal.core.resolver import Resolver
from pedal.environments import ALL_ENVIRONMENTS
from pedal.core.config_job import JobConfig
from dataclasses import dataclass, field

T = TypeVar("T", bound="EnvironmentConfig")

@dataclass
class EnvironmentConfig:
    job_config: JobConfig
    files: Dict[str, str]
    main_file: str
    main_code: str
    instructor_file: str
    # Metadata
    user: Any
    assignment: Any
    course: Any
    execution: Any
    # Legacy Tool settings
    skip_tifa: bool
    skip_run: bool
    real_io: bool
    path_mask: Optional[str]
    inputs: List[str]
    trace: bool
    threaded: bool
    # New Style Tool Settings
    tool: Dict[str, Dict]  # TODO: Make this happen
    # Resolver controls
    set_correct: bool
    set_success: bool
    resolver: Optional[Resolver] # TODO: Make this happen
    report: Report