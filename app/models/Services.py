from sqlmodel import SQLModel, Field


class Services(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    duration_in_minutes: int
    type_service: str
    price: float
