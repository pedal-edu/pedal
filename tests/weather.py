'''
Hello student. Thank you for downloading a CORGIS library. However, you do not need to open this library. Instead you should use the following:

    import weather
    
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
            'get': {"type": "ListType", "empty": False, 
                    "subtype": {"type": "NumType"}},
        
            'get_weather': {
                "type": "FunctionType", 
                "name": 'get_weather',
                "returns": 
		{"type": "ListType", "subtype": 
			{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Data'}, {"type": "LiteralStr", "value": 'Date'}, {"type": "LiteralStr", "value": 'Station'}], "values": [
				{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Precipitation'}, {"type": "LiteralStr", "value": 'Wind'}, {"type": "LiteralStr", "value": 'Temperature'}], "values": [
					{"type": "NumType"}, 
					{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Direction'}, {"type": "LiteralStr", "value": 'Speed'}], "values": [
						{"type": "NumType"}, 
						{"type": "NumType"}]}, 
					{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Min Temp'}, {"type": "LiteralStr", "value": 'Max Temp'}, {"type": "LiteralStr", "value": 'Avg Temp'}], "values": [
						{"type": "NumType"}, 
						{"type": "NumType"}, 
						{"type": "NumType"}]}]}, 
				{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Full'}, {"type": "LiteralStr", "value": 'Week of'}, {"type": "LiteralStr", "value": 'Month'}, {"type": "LiteralStr", "value": 'Year'}], "values": [
					{"type": "StrType"}, 
					{"type": "NumType"}, 
					{"type": "NumType"}, 
					{"type": "NumType"}]}, 
				{"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'State'}, {"type": "LiteralStr", "value": 'Code'}, {"type": "LiteralStr", "value": 'Location'}, {"type": "LiteralStr", "value": 'City'}], "values": [
					{"type": "StrType"}, 
					{"type": "StrType"}, 
					{"type": "StrType"}, 
					{"type": "StrType"}]}]}},
            }
        
        }
    }