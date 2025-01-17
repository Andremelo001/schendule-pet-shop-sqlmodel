from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.Services import Services

router = APIRouter(
    prefix="/services", 
    tags=["Services"],   
)

@router.post("/", response_model=Services)
def create_service(service: Services, session: Session = Depends(get_session)):
    """Endpoint para criar um novo serviço"""
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

@router.get("/", response_model=list[Services])
def read_services(offset: int = 0, limit: int = Query(default=10, le=100), 
               session: Session = Depends(get_session)):
    """Endpoint para listar todos os Serviços"""
    services = (select(Services).offset(offset).limit(limit))
    return session.exec(services).unique().all()

