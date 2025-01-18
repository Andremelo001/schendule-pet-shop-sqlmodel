from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Client import Client
    from .Schedule import Schedule

class PetUpdate(SQLModel):
    name: str | None
    breed: str | None
    age: int | None
    size_in_centimeters: int | None


class PetBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    breed: str
    age: int
    size_in_centimeters: int


class Pet(PetBase, table=True):
    client_id: int = Field(foreign_key="client.id")
    client: 'Client' = Relationship(back_populates="pets")
    schedules: list['Schedule'] = Relationship(back_populates="pet")


