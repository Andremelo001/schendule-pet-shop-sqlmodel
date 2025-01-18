from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.Pet import Pet



router = APIRouter(
    prefix="/pets", 
    tags=["Pets"],   
)

@router.post("/{client_id}/pet/", response_model=Pet)
def create_pet_for_client(client_id: int, pet: Pet, session: Session = Depends(get_session)):
    """Endpoint que cria um novo pet associado a um cliente"""
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
    statement = (select(Pet).offset(offset).limit(limit))
    return session.exec(statement).unique().all()

@router.get("/{client_id}/pets/", response_model=list[Pet])
def read_pet_for_client(client_id: int, session: Session = Depends(get_session)):
    """Endpoint que retorna um pet associado a um id de um cliente"""
    if not client_id:
            raise HTTPException(status_code=404, detail=f"Cliente com ID {client_id} não encontrado")
    return session.exec(select(Pet).where(Pet.client_id == client_id)).all()