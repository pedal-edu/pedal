#!/usr/bin/env python3
"""
Script to fix all the test_resolver.py tests to work with the new unified resolver format.
"""
import re

def fix_resolver_tests():
    # Read the file
    with open('/home/runner/work/pedal/pedal/tests/test_resolver.py', 'r') as f:
        content = f.read()
    
    # Replace direct simple.resolve() calls that aren't already updated
    # Pattern: final = simple.resolve()
    content = re.sub(
        r'^(\s*)final = simple\.resolve\(\)$',
        r'\1result = simple.resolve()\n\1final = self.get_final_from_result(result)',
        content,
        flags=re.MULTILINE
    )
    
    # Replace final.attribute with final['attribute'] but not e.final.attribute
    # Convert .success to ['correct'] since that's the new key name
    content = re.sub(r'(?<!e\.)final\.success\b', "final['correct']", content)
    content = re.sub(r'(?<!e\.)final\.message\b', "final['message']", content)
    content = re.sub(r'(?<!e\.)final\.title\b', "final['title']", content)
    content = re.sub(r'(?<!e\.)final\.category\b', "final['category']", content)
    content = re.sub(r'(?<!e\.)final\.score\b', "final['score']", content)
    content = re.sub(r'(?<!e\.)final\.label\b', "final['label']", content)
    
    # Write the file back
    with open('/home/runner/work/pedal/pedal/tests/test_resolver.py', 'w') as f:
        f.write(content)
    
    print("Updated test_resolver.py with unified format")

if __name__ == "__main__":
    fix_resolver_tests()