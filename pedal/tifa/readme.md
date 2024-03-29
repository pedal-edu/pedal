PyTIFA is the Python Type Inferencer and Flow Analyzer, also called just Tifa.

Tifa is meant to be used on simple programs written in learning situations,
in order to provide type information and detect certain common issues.
It makes some very strong assumptions and doesn't support all language features.

Tifa is supported by Skulpt. This means that Tifa is a Python library that
can be passed in a string of Python source code in order to traverse its
AST using underlying JavaScript libraries. If that isn't confusing,
then we invite you to make pull requests.

# Settings

## Type System Settings

[ ] Accept Generics for lists/dicts
[ ] Numeric type equality (float/int interchangeable?)
[ ] Which record type to accept?
[ ] Nominal or structural typing for records?
[ ] Evaluate string literals in type expressions?
[ ] Allow type changes for names

## Flow System Settings

[ ] Allow global writes
[ ] Allow unused variables (True, or a list of exceptions)

## Bad Code

[ ] Redundant ==True
[ ] Redundant elif/else empty body
[ ] Redundant IF/return
[ ] Unused return value
[ ] Unused expression value
[ ] Equality instead of assignment


# Examples of Assignments

```python
a = 0
grades = [1, 2, 3, 4]
grades[0] = 7

person = {'name': "Dr. Bart"}
person['name'] = "Cory Bart"

potions = [{"name": "Fire Breath", "rarity": 3}]
potions[0]['name'] = "Flame Breath"

from dataclasses import dataclass
@dataclass
class Dog:
    name: str
    age: int
    
ada = Dog("Ada", 4)
ada.name = "Ada Bart"

kennel = [ada]
kennel[0].age = 4 * 7



```