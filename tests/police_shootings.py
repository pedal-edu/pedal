'''
Hello! Thank you for downloading a CORGIS library. However, you do not
need to open this file. Instead you should make your own Python file and
add the following line:

import police_shootings

Then just place the files you downloaded alongside it.
'''

import os as _os
import pickle as _pickle

__all__ = ['get_shootings']

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
            'get_shootings': {
                "type": "FunctionType",
                "name": 'get_shootings',
                "returns": {
                    "type": "ListType", 
                    "empty": False, 
                    "subtype": {
                        "type": "DictType",
                        "literals": [
                            {"type": "LiteralStr", "value": "Person.Name"},
                            {"type": "LiteralStr", "value": "Person.Age"},
                            {"type": "LiteralStr", "value": "Person.Gender"},
                            {"type": "LiteralStr", "value": "Person.Race"},
                            {"type": "LiteralStr", "value": "Incident.Date.Month"},
                            {"type": "LiteralStr", "value": "Incident.Date.Day"},
                            {"type": "LiteralStr", "value": "Incident.Date.Year"},
                            {"type": "LiteralStr", "value": "Incident.Date.Full"},
                            {"type": "LiteralStr", "value": "Incident.Location.City"},
                            {"type": "LiteralStr", "value": "Incident.Location.State"},
                            {"type": "LiteralStr", "value": "Factors.Armed"},
                            {"type": "LiteralStr", "value": "Factors.Mental-Illness"},
                            {"type": "LiteralStr", "value": "Factors.Threat-Level"},
                            {"type": "LiteralStr", "value": "Factors.Fleeing"},
                            {"type": "LiteralStr", "value": "Shooting.Manner"},
                            {"type": "LiteralStr", "value": "Shooting.Body-Camera"},
                        ],
                        "values": [
                            {"type": "StrType"},
                            {"type": "NumType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "NumType"},
                            {"type": "NumType"},
                            {"type": "NumType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "BoolType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "StrType"},
                            {"type": "BoolType"},
                        ]
                    }
                }
            },
        }
    }
