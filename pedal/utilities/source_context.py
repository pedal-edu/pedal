"""
Utilities for extracting source code context from student submissions.
"""

import ast
from pedal.core.report import MAIN_REPORT
from pedal.core.location import Location


def find_function_definition(function_name, report=MAIN_REPORT):
    """
    Find the definition location of a function in the student's source code.
    
    Args:
        function_name (str): The name of the function to find.
        report (Report): The report containing the source AST.
    
    Returns:
        Location or None: The location of the function definition, or None if not found.
    """
    if 'source' not in report or not report['source']['ast']:
        return None
    
    student_ast = report['source']['ast']
    
    for node in ast.walk(student_ast):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return Location(line=node.lineno, col=node.col_offset, 
                          end_line=getattr(node, 'end_lineno', None),
                          end_col=getattr(node, 'end_col_offset', None))
    
    return None


def get_source_line_context(location, report=MAIN_REPORT, context_lines=0):
    """
    Get source code lines around a given location.
    
    Args:
        location (Location): The location to get context for.
        report (Report): The report containing the submission.
        context_lines (int): Number of lines before/after to include (0 = just the target line).
    
    Returns:
        str or None: The source code context, or None if not available.
    """
    if not location:
        return None
        
    if 'source' not in report:
        return None
        
    # Get the main submission
    submission = report.submission
    if not submission or not submission.main_file or not submission.files:
        return None
    
    # Get the source code 
    main_file_key = submission.main_file
    if main_file_key not in submission.files:
        return None
        
    source_code = submission.files[main_file_key]
    if not source_code:
        return None
    
    lines = source_code.splitlines()
    
    # Convert to 0-based indexing
    target_line = location.line - 1
    start_line = max(0, target_line - context_lines)
    end_line = min(len(lines), target_line + context_lines + 1)
    
    if target_line >= len(lines):
        return None
        
    context_lines_list = lines[start_line:end_line]
    return "\n".join(context_lines_list)


def format_source_context_for_function(function_name, report=MAIN_REPORT):
    """
    Get formatted source context for a function definition.
    
    Args:
        function_name (str): The name of the function.
        report (Report): The report to use.
    
    Returns:
        str or None: Formatted context string, or None if not available.
    """
    location = find_function_definition(function_name, report)
    if not location:
        return None
        
    context = get_source_line_context(location, report, context_lines=0)
    if not context:
        return None
        
    formatter = report.format if hasattr(report, 'format') else None
    if formatter and hasattr(formatter, 'line') and hasattr(formatter, 'python_code'):
        return f"In your function {formatter.name(function_name)} on line {formatter.line(location.line)}:\n{formatter.python_code(context)}"
    else:
        return f"In your function '{function_name}' on line {location.line}:\n{context}"