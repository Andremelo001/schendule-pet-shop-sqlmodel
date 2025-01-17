from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pet import Pet
    from .schedule import Schedule


class ClientBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    cpf: str = Field(unique=True)
    age: int
    is_admin: bool


class Client(ClientBase, table=True):
    pets: list['Pet'] = Relationship(back_populates="client")
    schedules: list['Schedule'] = Relationship(back_populates="client")
