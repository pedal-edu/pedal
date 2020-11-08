import os
import sys
from textwrap import indent, dedent


def parse_out_file(path):
    """
    Parses an out file, which is based on ``ini`` files. They have pretty
    basic syntax. The difference from what configparser is that indentation
    is preserved in multiline values. We don't support comments and a number
    of other features, but who needs 'em.

    Args:
        contents (str): The contents of the out file.

    Returns:
        dict[str, dict[str, str]]: The constructed out sections=>{fields=>data}
    """
    sections = {'default': {}}
    current_section = 'default'
    current_key = None
    multiline = False
    with open(path) as outfile:
        for line in outfile:
            if line.startswith('['):
                multiline = False
                current_section = line.strip()[1:-1]
                sections[current_section] = {}
            elif line.startswith('    '):
                sections[current_section][current_key] += line[4:]
            elif line.strip():
                multiline = False
                parts = line.split(":", maxsplit=1)
                current_key = parts[0].rstrip()
                sections[current_section][current_key] = ""
                if len(parts) == 1 or not parts[1].lstrip():
                    multiline = True
                else:
                    sections[current_section][current_key] += parts[1].strip()
            elif multiline:
                sections[current_section][current_key] += "\n"
    return sections


def generate_out_file(outfile, sections):
    for section_name, section in sections.items():
        outfile.write(f"[{section_name}]\n")
        for field, value in section.items():
            outfile.write(f"{field}:")
            value = str(value)
            if '\n' in value:
                outfile.write("\n")
                for line in value.split("\n"):
                    outfile.write(f"    {line}\n")
            else:
                outfile.write(f" {value}\n")


def _make_final(environment):
    """ Determine the final environment's section """
    if environment is None:
        return 'final'
    else:
        return f"{environment}.final"


class ReportVerifier:
    """ Helper class for reading and processing a '.out' file. """
    def __init__(self, path, environment):
        self.outfile = parse_out_file(path)
        self.environment = environment

    def get_final(self):
        """ Get the expected final feedback. """
        final_environment = _make_final(self.environment)
        if final_environment in self.outfile:
            return self.outfile[final_environment].items()
        elif 'final' in self.outfile:
            return self.outfile['final'].items()
        return {}


def generate_report_out(path, environment, report):
    result = {}
    # Allow graceful appending
    if path is not None and os.path.exists(path):
        result = parse_out_file(path)
    final_environment = _make_final(environment)
    try:
        fields = report.result.to_json()
    except Exception as e:
        raise report
    # TODO: Hack, just remove the data field for simplicity - fix this later
    fields.pop('data')
    fields.pop('hide_correctness')
    result[final_environment] = fields
    # TODO: Support ``forbid`` and ``available`` fields for finer grained
    #   output checking.
    if path is not None:
        with open(path, 'w') as outfile:
            generate_out_file(outfile, result)
    else:
        generate_out_file(sys.stdout, result)
        return result
