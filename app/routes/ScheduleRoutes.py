from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from app.database import get_session
from app.models.Services import Services
from app.models.Schedule import Schedule, ScheduleServices, ScheduleWithClientPetServices
from sqlalchemy import func
from datetime import datetime


router = APIRouter(
    prefix="/schedules", 
    tags=["Schedules"],  
)

@router.post("/", response_model=Schedule)
def create_schedule(schedule: Schedule, service_ids: list[int], session: Session = Depends(get_session)):
    
    if isinstance(schedule.date_schedule, str):
        schedule.date_schedule = datetime.fromisoformat(schedule.date_schedule.replace("Z", "+00:00"))
    
    if schedule.id == 0:
        max_id = session.query(func.max(Schedule.id)).scalar()
        schedule.id = max_id + 1 if max_id is not None else 1

    session.add(schedule)
    session.commit()
    session.refresh(schedule)

    for service_id in service_ids:
        service = session.get(Services, service_id)
        if not service:
            raise HTTPException(status_code=404, detail=f"Serviço com ID {service_id} não encontrado")
        
        association = ScheduleServices(schedule_id=schedule.id, services_id=service_id)
        session.add(association)

    session.commit()

    schedule = session.query(Schedule).filter(Schedule.id == schedule.id).first()

    return schedule

@router.get("/", response_model=list[ScheduleWithClientPetServices])
def read_schedules(offset: int = 0, limit: int = Query(default=10, le=100), 
               session: Session = Depends(get_session)):
    """Endpoint que retorna os agendamentos com as informaçãoes do cliente e do pet associado"""
    statement = (select(Schedule).offset(offset).limit(limit)
                 .options(joinedload(Schedule.client), joinedload(Schedule.pets), 
                          joinedload(Schedule.services)))
    return session.exec(statement).unique().all()