from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
    from .schedule import Schedule


class PetBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    breed: str
    age: int
    size_in_centimeters: int


class Pet(PetBase, table=True):
    client_id: int = Field(foreign_key="client.id")
    client: 'Client' = Relationship(back_populates="pets")
    schedules: list['Schedule'] = Relationship(back_populates="pets")


