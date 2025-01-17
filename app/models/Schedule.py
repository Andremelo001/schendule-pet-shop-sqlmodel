from sqlmodel import SQLModel, Field, Relationship
from app.models.Client import ClientBase, Client
from app.models.Pet import PetBase, Pet
from app.models.Services import Services


class ScheduleServices(SQLModel, table=True):
    services_id: int = Field(
        default=None, foreign_key="services.id", primary_key=True
    )
    schedule_id: int = Field(
        default=None, foreign_key="schedule.id", primary_key=True
    )


class ScheduleBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    #vê se tu consegue arrumar essa parte de inserir uma data, ele ta dando erro por conta do formato
    #date_schedule: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Schedule(ScheduleBase, table=True):
    client_id: int = Field(foreign_key="client.id")
    pet_id: int = Field(foreign_key="pet.id")
    client: 'Client' = Relationship(back_populates="schedules")
    pets: 'Pet' = Relationship(back_populates="schedules")
    services: list['Services'] = Relationship(link_model=ScheduleServices)


class ScheduleWithClientPetServices(ScheduleBase):
    client: 'ClientBase'
    pets: 'PetBase'
    services: list['Services']


ScheduleWithClientPetServices.model_rebuild()



