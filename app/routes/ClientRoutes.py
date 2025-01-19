from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from app.models.Client import Client, ClientBaseWithPets
from app.database import get_session
from sqlalchemy import func
from app.models.Schedule import Schedule, ScheduleBase
from app.models.Pet import Pet

router = APIRouter(
    prefix="/clients",  
    tags=["Clients"],   
)

@router.post("/", response_model=Client)
def creat_client(client: Client, session: Session = Depends(get_session)):
    """Endpoint para criar um novo Cliente"""
    if client.id == 0:
        max_id = session.query(func.max(Client.id)).scalar()
        client.id = max_id + 1 if max_id is not None else 1

    existing_client = session.exec(select(Client).where(Client.cpf == client.cpf)).first()
    if existing_client:
        raise HTTPException(
            status_code=400, detail=f"O CPF '{client.cpf}' já está cadastrado."
        )

    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/", response_model=list[ClientBaseWithPets])
def read_clients(offset: int = 0, limit: int = Query(default=10, le=100), 
                 session: Session = Depends(get_session)):
    """Endpoint que retorna todos os clientes e seus pets"""
    statement = (select(Client).offset(offset).limit(limit)
                 .options(joinedload(Client.pets))) 
    return session.exec(statement).unique().all()


@router.get("/{client_id}", response_model=ClientBaseWithPets)
def get_client_by_id(client_id: int, session: Session = Depends(get_session)):
    """Endpoint que retorna um cliente e seus pets a partir de um `client_id`"""
    statement = (
        select(Client)
        .where(Client.id == client_id)
        .options(joinedload(Client.pets))
    )

    client = session.exec(statement).first()

    if not client:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {client_id} não encontrado")

    return client

@router.put("/{client_id}", response_model=Client)
def update_client(client_id: int, client: Client, session: Session = Depends(get_session)):
    """Endpoint que atualiza os dados de um cliente a partir de um `client_id`"""
    db_client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    for key, value in client.model_dump(exclude_unset=True).items():
        setattr(db_client, key, value)

    session.commit() 
    session.refresh(db_client)

    return db_client

@router.delete("/{client_id}")
def delete_client(client_id: int, session: Session = Depends(get_session)):
    """Endpoint que deleta um cliente, seus pets e os agendamentos que estão associados a ele a partir de um `client_id`"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    schedules_to_delete = session.query(Schedule).filter(Schedule.client_id == client_id).all()
    for schedule in schedules_to_delete:
        session.delete(schedule)
    
    pets_to_delete = session.query(Pet).filter(Pet.client_id == client_id).all()
    for pet in pets_to_delete:
        session.delete(pet)

    session.delete(client)
    session.commit()

    return {"ok": True}

@router.get("/get_schedule/{client_id}", response_model=list[ScheduleBase])
def get_client_schedules(client_id: int, session: Session = Depends(get_session)):
    """Endpoint que realiza a busca dos agendamentos que estão associados ao cliente por um `client_id`"""
    # Buscar o cliente
    statement = select(Client).where(Client.id == client_id)
    client = session.exec(statement).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar os agendamentos do cliente
    schedules = session.exec(select(Schedule).where(Schedule.client_id == client_id)).all()

    if not schedules:
        raise HTTPException(status_code=404, detail="Nenhum agendamento encontrado para este cliente")

    return schedules