import os, sys
from pprint import pprint

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, pedal_library)


from pedal import set_source, find_match, tifa_analysis


# set_source("""
# highest = 0
# if False:
#     0
# else:
#     if False:
#         0
#     else:
#         highest = 0
# highest""")

#t = tifa_analysis()
#pprint(t.name_map)

#pprint(t.report['tifa']['issues'])

'''
set_source(('Dog = {"Name": str, "Age": int, "Fluffy": bool}\n'
            'def do_stuff(a_dog: Dog) -> Dog:\n'
            '    a_dog["Name"]+""\n'
            '    a_dog["Age"]+5\n'
            '    return a_dog\n'
            'ada = {"Name": "Ada", "Age": 2, "Fluffy": True}\n'
            'do_stuff(ada)["Name"] + ""\n'
            'do_stuff(ada)["Age"] + 0'))
'''
set_source('''
def count_words(words: str) -> {str: int}:
    counts = {}
    for word in words.split(","):
        if word not in counts:
            counts[word] = 0
        counts[word] += 1
    return counts

count_words("alpha,alpha,beta,alpha")''')

t = tifa_analysis()
pprint(t.name_map)

if t.report['tifa']['success']:
    pprint(t.report['tifa']['issues'])
else:
    print("EXCEPTION")
    print(t.report['tifa']['error'])