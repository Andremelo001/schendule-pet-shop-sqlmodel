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

@router.get("/total", response_model=int)
def get_total_schedules(session: Session = Depends(get_session)):
    total_schedules = session.exec(select(func.count(Schedule.id))).one()
    return total_schedules
    

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
    statement = (select(Schedule).offset(offset).limit(limit)
                 .options(joinedload(Schedule.client), joinedload(Schedule.pet), 
                          joinedload(Schedule.services)))
    return session.exec(statement).unique().all()

@router.get("/{schedule_id}", response_model=ScheduleWithClientPetServices)  # Usando o modelo correto
def get_schedule_by_id(schedule_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(
            joinedload(Schedule.client),
            joinedload(Schedule.pet),
            joinedload(Schedule.services),
        )
    )

    schedule = session.exec(statement).first()

    if not schedule:
        raise HTTPException(status_code=404, detail=f"Agendamento com ID {schedule_id} não encontrado")

    return schedule

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session.delete(schedule)
    session.commit()
    return {"ok": True}


@router.put("/{schedule_id}", response_model=Schedule)
def update_schedule(schedule_id: int, schedule: Schedule, session: Session = Depends(get_session)):
    db_schedule = session.get(Schedule, schedule_id)

    if not db_schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    update_data = schedule.model_dump(exclude_unset=True)

    if "date_schedule" in update_data and isinstance(update_data["date_schedule"], str):
        update_data["date_schedule"] = datetime.fromisoformat(update_data["date_schedule"].replace("Z", "+00:00"))

    for key, value in update_data.items():
        setattr(db_schedule, key, value)

    session.commit()
    session.refresh(db_schedule)

    return db_schedule


@router.get("/{year}/{month}", response_model=list[ScheduleWithClientPetServices])
def get_schedules_by_month(
    year: int,
    month: int,
    session: Session = Depends(get_session)
):
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida. Verifique o ano e o mês informados.")

    statement = (
        select(Schedule)
        .where(Schedule.date_schedule >= start_date, Schedule.date_schedule < end_date)
        .options(
            joinedload(Schedule.client),
            joinedload(Schedule.pet),
            joinedload(Schedule.services)
        )
    )

    schedules = session.exec(statement).unique().all()

    if not schedules:
        raise HTTPException(status_code=404, detail=f"Nenhum agendamento encontrado para {month}/{year}")

    return schedules

