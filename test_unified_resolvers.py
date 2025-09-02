#!/usr/bin/env python3
"""
Test script to validate the current resolver behavior and test the unified approach.
"""

from pedal.core.commands import clear_report, explain, gently, give_partial
from pedal.resolvers import simple, statistics, sectional, full, silent
from pedal.core.final_feedback import FinalFeedback


def test_current_resolver_behaviors():
    """Test what each resolver currently returns."""
    print("=== Current Resolver Behaviors ===")
    
    # Test simple resolver
    clear_report()
    explain('This is a test message')
    simple_result = simple.resolve()
    print(f"Simple resolver: {type(simple_result)} - {simple_result}")
    
    # Test statistics resolver
    clear_report()
    explain('This is a test message')
    stats_result = statistics.resolve()
    print(f"Statistics resolver: {type(stats_result)}")
    if isinstance(stats_result, dict):
        print(f"  Keys: {list(stats_result.keys())}")
        if 'final' in stats_result:
            print(f"  Final type: {type(stats_result['final'])}")
        if 'considered' in stats_result:
            print(f"  Considered length: {len(stats_result['considered'])}")
    
    # Test full resolver  
    clear_report()
    explain('This is a test message')
    full_result = full.resolve()
    print(f"Full resolver: {type(full_result)} - {full_result}")
    
    # Test sectional resolver
    clear_report()
    explain('This is a test message')
    sectional_result = sectional.resolve()
    print(f"Sectional resolver: {type(sectional_result)}")
    if isinstance(sectional_result, dict):
        print(f"  Keys: {list(sectional_result.keys())}")
    
    # Test silent resolver
    clear_report()
    explain('This is a test message')
    silent_result = silent.resolve()
    print(f"Silent resolver: {type(silent_result)} - {repr(silent_result)}")
    

def test_proposed_unified_format():
    """Test what the proposed unified format should look like."""
    print("\n=== Proposed Unified Format ===")
    
    clear_report()
    explain('Test message')
    give_partial(0.5, message="Partial credit")
    gently('A gentle message')
    
    # This is what the unified format should look like
    proposed_format = {
        'final': None,  # Would be the final feedback as JSON
        'considered': []  # Would be all considered feedback as JSON
    }
    print(f"Proposed format structure: {list(proposed_format.keys())}")


if __name__ == "__main__":
    test_current_resolver_behaviors()
    test_proposed_unified_format()