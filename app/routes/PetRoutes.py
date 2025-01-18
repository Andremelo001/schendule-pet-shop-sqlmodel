from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.database import get_session
from app.models.Pet import Pet, PetUpdate
from app.models.Client import Client
from app.models.Schedule import ScheduleServices, Schedule


router = APIRouter(
    prefix="/pets", 
    tags=["Pets"],   
)

@router.post("/{client_id}/pet/", response_model=Pet)
def create_pet_for_client(client_id: int, pet: Pet, session: Session = Depends(get_session)):
    """Endpoint que cria um novo pet associado a um cliente"""
    statement = (select(Client).options(joinedload(Client.pets)).where(Client.id == client_id))

    client = session.exec(statement).unique().all()

    if not client:
         raise HTTPException(status_code=404, detail=f"Client com o ID {client_id} não encontrado")
         
    pet.client_id = client_id
    session.add(pet)
    session.commit()
    session.refresh(pet)
    return pet

@router.get("/", response_model=list[Pet])
def read_pets(offset: int = 0, limit: int = Query(default=10, le=100), 
               session: Session = Depends(get_session)):
    """Endpoint que retorna todos os pets cadastrados no sistema, 
    utilizando do offset e do limit para restriguir a quantidades de pets retornados"""
    statement = select(Pet)

    pets = session.exec(statement).all()

    if not pets:
         raise HTTPException(status_code=404, detail="Nenhum pet cadastrado")
    
    statement = (select(Pet).offset(offset).limit(limit))
    return session.exec(statement).unique().all()

@router.get("/{client_id}", response_model=list[Pet])
def read_pet_for_client(client_id: int, session: Session = Depends(get_session)):
    """Endpoint que retorna um pet associado a um id de um cliente"""

    statement = (select(Client).options(joinedload(Client.pets)).where(Client.id == client_id))

    client = session.exec(statement).first()

    if not client:
            raise HTTPException(status_code=404, detail=f"Cliente com ID {client_id} não encontrado")
    
    return client.pets

@router.delete("/{client_id}/pets/{pet_id}")
def delete_pet_for_client(client_id: int, pet_id: int, session: Session = Depends(get_session)):
     """Endpoint que deleta o pet pelo id do cliente fornecido"""
     pet = session.get(Pet, pet_id)

     if not pet or pet.client_id != client_id:
          raise HTTPException(status_code=404, detail="Pet não encontrado")
     
     schedules = session.exec(select(Schedule).where(Schedule.pet_id == pet_id)).all()

     for schedule in schedules:
          
          scheduleService = session.exec(select(ScheduleServices).where(ScheduleServices.schedule_id == schedule.id)).all()

          for schedule_service in scheduleService:
               session.delete(schedule_service)

          session.delete(schedule)
     
     session.delete(pet)
     session.commit()
     return {"ok": True}

@router.put("/{client_id}/pets/{pet_id}")
def update_pet_for_client(client_id: int, pet_id: int, pet_update: PetUpdate, session: Session = Depends(get_session)):
     """Endpoint que realiza a atualização de dados de um pet"""

     statement = select(Pet).where(Pet.id == pet_id)

     pet = session.exec(statement).first()

     if not pet or pet.client_id != client_id:
          raise HTTPException(status_code=404, detail="Pet não encontrado")
     
     for key, value in pet_update.model_dump(exclude_unset=True).items():
          setattr(pet, key, value)
    
     session.add(pet)
     session.commit()
     session.refresh(pet)

     return pet


    

     
     