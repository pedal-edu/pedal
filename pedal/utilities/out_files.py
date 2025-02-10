def parse_out_file(path):
    """
    Parses an out file, which is based on ``ini`` files. They have pretty
    basic syntax. The difference from what configparser is that indentation
    is preserved in multiline values. We also support comments.

    Args:
        path (str): The path to the inifile that will be read.

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
            elif line.lstrip().startswith('#') or line.lstrip().startswith(';'):
                continue
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
    """
    Writes data to an output file in a structured format.

    This function takes an output file target and a dictionary of sections. Each section
    is written to the file as a header followed by its corresponding fields and
    values in key-value pair format. Line breaks in values are preserved, and values
    with line breaks are split for better readability in the file.

    Args:
        outfile: An open writable file object where the sections will be written.
        sections (dict): A mapping where each key is a section name (str), and the value
            is a dictionary containing fields (keys as strings) and their corresponding
            values. Values can contain newline characters for multiline entries.

    Returns:
        None
    """
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
