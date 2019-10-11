import os, sys
from pprint import pprint

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.tifa.tifa import Tifa

tifa = Tifa()

tifa.process_code('''
v = 14
v = '14'
v = False
''')

pprint(tifa.report['tifa']['top_level_variables']['v'].type)

from pedal import set_source, find_match

set_source("var = 14\n"
           "var = '14'\n"
           "var = False\n")
match = find_match("_var_")
data_state = match['_var_']
data_state = match['_var_'].get_data_state()
print(data_state.type) #UnknownType
print(data_state.trace[0].type)#StrType
print(data_state.trace[0].trace[0].type)#NumType