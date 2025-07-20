"""
Configuration support for Pedal!

Pedal users should be able to specify configuration in all the following ways:
- Via a configuration file (pedal.config, or CLI parameter)
- Via environment variables
- Via a cli args
- Via keyword arguments to the main Pedal entry point functions
- Via a configuration object

We can use argparse.parse_known_args() to parse the command line arguments.

Pedal is used to execute a Job, which has one or more Bundles.
Jobs are executed through one of the Pipelines, which are different modes.
Jobs are configured via JobConfig, either through the CLI or a config file.

Bundle executions occurs in an Environment, with a submission and ICS.
The result will be a BundleResult, which has data, output, errors, and resolution.

An EnvironmentConfig determines how a Bundle is executed.
The Job sets up the EnvironmentConfig, to dispatch to the setup_environment.
"""

import argparse
from collections import defaultdict
from typing import Optional, List, Dict, Any, Type, TypeVar
from pedal.command_line.modes import MODES
from dataclasses import dataclass, field

from pedal.environments import ALL_ENVIRONMENTS
from pedal.utilities.out_files import parse_out_file


def metadata(help: str, choices: List[str] = None,
             optional: bool = True, short_form: str = None,
             nargs: str = None, action: str = 'store'):
    # Build up a typesafe dictionary from the arguments
    result = {
        "help": help,
        "optional": optional,
        "short_form": short_form,
        "action": action
    }
    if action not in ('store_true', 'store_false'):
        result['choices'] = choices
        result["nargs"] = nargs
    return result


T = TypeVar("T", bound="EnvironmentConfig")

MAIN_PARSER_DESCRIPTION = "Run instructor control script on student submission."

@dataclass
class JobConfig:
    mode: MODES = field(
        metadata=metadata(
            optional=False,
            help="What kind of Pedal analysis you're running. See the description of each mode above.",
            choices=list(MODES.PIPELINES)
        )
    )
    # This field is only required if we're in reduced mode.
    instructor: Optional[str] = field(
        metadata=metadata(
            optional=False,
            help='The path to the instructor control script, or multiple scripts.'
        )
    )
    submissions: str = field(
        default="submissions",
        metadata=metadata(
            optional=False,
            help='The path to the student submissions.'
                        ' Defaults to a folder named '
                        'submissions adjacent to the '
                        'instructor control script.',
            nargs="?"
        )
    )
    alternate_filenames: str = field(
        default="",
        metadata=metadata(
            help="A semicolon separated list of potential filenames to try if the main isn't found.",
        )
    )
    config: Optional[str] = field(
        default=None,
        metadata=metadata(
            help="Uses the configuration file to get settings."
        )
    )
    output: str = field(
        default="stdout",
        metadata=metadata(
            help='The output file path for the result of the instructor script (not the student executions output). Defaults to stdout.',
            short_form="o"
        )
    )
    create_output: bool = field(
        default=False,
        metadata=metadata(
            help="In verify mode, creates any missing outputs.",
            short_form="m",
            action="store_true"
        )
    )
    environment: str = field(
        default="standard",
        metadata=metadata(
            help="Sets the environment context for this script, which"
                 " can run special setups and override tools as"
                 " needed.",
            choices=ALL_ENVIRONMENTS
        )
    )
    instructor_name: str = field(
        default=None,
        metadata=metadata(
            help="Sets the name of the instructor file to something"
                 " more friendly. If not given, then will default"
                 " to the instructor filename.",
        )
    )
    progsnap_profile: str = field(
        default="blockpy", # TODO: Change this biased default
        metadata=metadata(
            help="Uses the given profile's default settings for"
                 " loading in a ProgSnap2 dataset",
        )
    )
    include_scripts: Optional[str] = field(
        default=None,
        metadata=metadata(
            help="An optional filter to only include certain scripts",
        )
    )
    limit: Optional[int] = field(
        default=None,
        metadata=metadata(
            help="An optional limit to how many submissions are run. Mostly for testing purposes.",
        )
    )
    resolver: str = field(
        default="resolve",
        metadata=metadata(
            help="Choose a different resolver to use (the name of a function defined in the instructor control script).",
        )
    )
    submission_direct: bool = field(
        default=False,
        metadata=metadata(
            help="Give the student code directly instead of loading from a file.",
            action="store_true"
        )
    )
    instructor_direct: bool = field(
        default=False,
        metadata=metadata(
            help="Give the instructor code directly instead of loading from a file.",
            action="store_true"
        )
    )
    skip_tifa: bool = field(
        default=False,
        metadata=metadata(
            help="Skip using TIFA in the environment",
            action="store_true"
        )
    )
    skip_run: bool = field(
        default=False,
        metadata=metadata(
            help="Skip automatically running student code in the environment",
            action="store_true"
        )
    )
    progsnap_events: str = field(
        default="run",
        metadata=metadata(
            help="Choose what level of event to capture from Progsnap event logs.",
            choices=["run", "edit", "last", "compile"]
        )
    )
    cache: Optional[str] = field(
        default=None,
        metadata=metadata(
            help="Use the given directory to hold the cache."
                 " You can use './' to use the current directory.",
        )
    )
    threaded: bool = field(
        default=False,
        metadata=metadata(
            help="Run the instructor script in a separate thread to avoid"
                 " timeout crashes.",
            action="store_true"
        )
    )
    log_level: str = field(
        default="ERROR",
        metadata=metadata(
            help="Set the logging level for Pedal.",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
    )

    tool: Dict[str, Dict[str, Any]] = field(
        default_factory=dict,
        metadata=metadata(
            help="Additional configuration for specific tools. Provide"
                        " them in the format `-- tool name.setting=value`, e.g.,"
                        " `--tool tifa.skip=true`.",
            nargs="*"
        )
    )

def parse_nested_dict(items):
    """Convert ['sandbox.trace=true', 'tifa.allow_none_objects=true'] into a nested dict"""
    nested_dict = defaultdict(dict)
    print(items)
    for item in items:
        if '=' not in item:
            raise ValueError(f"Invalid format: {item}. Expected key=value.")
        key, value = item.split('=', 1)
        parts = key.split('.')
        if len(parts) < 2:
            raise ValueError(f"Invalid tool key: {key}. Must be in format 'name.setting'.")
        tool_name, setting = parts[0], '.'.join(parts[1:])
        nested_dict[tool_name][setting] = value
    return dict(nested_dict)


def parse_config_file(path):
    config_data = parse_out_file(path)
    defaults = config_data.pop("default")

    for section_name, items in config_data.items():
        if section_name.startswith("tool."):
            tool_name = section_name[5:]
            if not tool_name:
                raise ValueError("Tool name cannot be empty.")
            defaults[tool_name] = items
        else:
            raise ValueError(f"Unknown config section: {section_name}")

    return defaults



def make_job_config_parser():
    # Root parser, that will be extended with the real parser.
    # This allows us to extract out the config file first.
    config_parser = argparse.ArgumentParser(description=MAIN_PARSER_DESCRIPTION,
                                            add_help=False)
    config_parser.add_argument("--config", "-c",
                               help="Uses the configuration file to get settings.")
    args, remaining_argv = config_parser.parse_known_args()

    defaults = {}
    if args.config:
        # Parse the config file, update the defaults accordingly
        defaults.update(parse_config_file(args.config))

    parser = argparse.ArgumentParser(description=MAIN_PARSER_DESCRIPTION,
                                     parents=[config_parser])

    fields = [field for field in JobConfig.__dataclass_fields__.items()
              if field[0] != "config"]
    for field_name, field_obj in fields:
        meta = field_obj.metadata

        names = ["--" + field_name] if meta["optional"] else [field_name]
        if meta["short_form"]:
            names.append("-" + meta["short_form"])
        default_function = field_obj.default_factory() if callable(field_obj.default_factory) else field_obj.default
        parameters = {
            "help": meta["help"],
            "action": meta["action"]
        }
        if "choices" in meta:
            parameters["choices"] = meta["choices"]
        if "nargs" in meta:
            parameters["nargs"] = meta["nargs"]
        parser.add_argument(*names,
                            default=default_function,
                            **parameters
                            )

    parser.set_defaults(**defaults)

    # Reset `required` attribute when provided from config file
    for action in parser._actions:
        if action.dest in defaults:
            action.required = False

    parsed_args = parser.parse_args(remaining_argv)

    # Post process
    parsed_args.tool = parse_nested_dict(parsed_args.tool or [])

    return JobConfig(**vars(parsed_args))
