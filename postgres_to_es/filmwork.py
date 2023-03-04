from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class Person:
    id: UUID
    name: str


class Filmwork(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    rating: float | None = 0.0
    genres: set[str] = set()
    actors: set[Person] = set()
    writers: set[Person] = set()
    directors: set[Person] = set()
