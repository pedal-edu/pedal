import os
import sys

from pedal.utilities.out_files import parse_out_file, generate_out_file


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
