from sqlalchemy.orm import joinedload
from app.models.Client import Client
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.Pet import PetBase

router = APIRouter(
    prefix="/endpoints",  
    tags=["Endpoints"],   
)


@router.get("/{client_id}", response_model=list[PetBase])
def get_pets_by_client(client_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Client)
        .where(Client.id == client_id)
        .options(joinedload(Client.pets))
    )

    client = session.exec(statement).first()

    if not client:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {client_id} não encontrado")

    if not client.pets:
        raise HTTPException(status_code=404, detail=f"Nenhum pet encontrado para o cliente com ID {client_id}")

    return client.pets