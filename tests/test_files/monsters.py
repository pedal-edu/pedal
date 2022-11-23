from dataclasses import dataclass


@dataclass
class Monster:
    name: str
    age: int
    kind: str

dracula = Monster("Dracula", 307, "vampire")
