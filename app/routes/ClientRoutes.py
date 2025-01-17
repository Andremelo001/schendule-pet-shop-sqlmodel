from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from app.models.client import Client
from app.database import get_session

router = APIRouter(
    prefix="/clients",  
    tags=["Clients"],   
)

@router.post("/", response_model=Client)
def creat_client(client: Client, session: Session = Depends(get_session)):
    """Endpoint para criar um novo Cliente"""
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/", response_model=list[Client])
def read_client(offset: int = 0, limit: int = Query(default=10, le=100), 
               session: Session = Depends(get_session)):
    """Endpoitn que retorna todos os clientes cadastrados"""
    statement = (select(Client).offset(offset).limit(limit)
                 .options(joinedload(Client.pets), joinedload(Client.schedules)))
    return session.exec(statement).unique().all()
