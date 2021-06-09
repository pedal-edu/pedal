from typing import TypedDict


class Movie(TypedDict):
    name: str
    year: int


def exclaim(a_movie: Movie) -> str:
    return a_movie['name'] + "!"


print(exclaim({"name": "Hello World", "year": 2021}))

print(Movie['name'])
