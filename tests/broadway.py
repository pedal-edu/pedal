'''
Hello student. Thank you for downloading a CORGIS library. However, you do not need to open this library. Instead you should use the following:

    import broadway
    
If you opened the file because you are curious how this library works, then well done! We hope that you find it a useful learning experience. However, you should know that this code is meant to solve somewhat esoteric pedagogical problems, so it is often not best practices. 
'''

import sys as _sys
import os as _os
import json as _json
import sqlite3 as _sql
import difflib as _difflib

def _tifa_definitions():
    return {"type": "ModuleType",
        "fields": {
            'get': {
                "type": "FunctionType",
                "name": 'get',
                "returns": {
                    "type": "ListType", 
                    "empty": False, 
                    "subtype": {"type": "NumType"}
                }
            },
        
            'get_shows': {
                "type": "FunctionType", 
                "name": 'get_shows',
                "returns": 
        {"type": "ListType", "subtype":
            {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Date'}, {"type": "LiteralStr", "value": 'Show'}, {"type": "LiteralStr", "value": 'Statistics'}], "values": [
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Month'}, {"type": "LiteralStr", "value": 'Year'}, {"type": "LiteralStr", "value": 'Day'}, {"type": "LiteralStr", "value": 'Full'}], "values": [
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "StrType"}]},
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Theatre'}, {"type": "LiteralStr", "value": 'Type'}, {"type": "LiteralStr", "value": 'Name'}], "values": [
                    {"type": "StrType"},
                    {"type": "StrType"},
                    {"type": "StrType"}]},
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Performances'}, {"type": "LiteralStr", "value": 'Gross'}, {"type": "LiteralStr", "value": 'Gross Potential'}, {"type": "LiteralStr", "value": 'Capacity'}, {"type": "LiteralStr", "value": 'Attendance'}], "values": [
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"}]}]}},
            },

            'get_production': {
                "type": "FunctionType",
                "name": 'get_shows',
                "returns":
        {"type": "ListType", "subtype":
            {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Date'}, {"type": "LiteralStr", "value": 'Show'}, {"type": "LiteralStr", "value": 'Statistics'}], "values": [
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Month'}, {"type": "LiteralStr", "value": 'Year'}, {"type": "LiteralStr", "value": 'Day'}, {"type": "LiteralStr", "value": 'Full'}], "values": [
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "StrType"}]},
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Theatre'}, {"type": "LiteralStr", "value": 'Type'}, {"type": "LiteralStr", "value": 'Name'}], "values": [
                    {"type": "StrType"},
                    {"type": "StrType"},
                    {"type": "StrType"}]},
                {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Performances'}, {"type": "LiteralStr", "value": 'Gross'}, {"type": "LiteralStr", "value": 'Gross Potential'}, {"type": "LiteralStr", "value": 'Capacity'}, {"type": "LiteralStr", "value": 'Attendance'}], "values": [
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"},
                    {"type": "NumType"}]}]}},
            }
        
        }
    }
