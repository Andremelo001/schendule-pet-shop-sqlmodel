```mermaid
classDiagram
    direction LR
    class Client {
        id: UUID 
        name: str
        cpf: str
        age: int
        is_admin: bool
    }

    class Pet {
        id: UUID
        name: str
        breed: str
        age: int
        size_in_centimeters: int
        id_client: UUID
    }

    class Schedule {
        id: UUID
        date_schedule: date
        id_client: UUID
        id_service: UUID
        id_pet: UUID
    }

    class Services {
        id: UUID
        duration: int
        type_service: str
        price: float
    }

    Client "1" -- "*" Pet
    Client "1" -- "*" Schedule
    Schedule "*" --> "*" Services
    Schedule "*" -- "1" Pet
``` 
