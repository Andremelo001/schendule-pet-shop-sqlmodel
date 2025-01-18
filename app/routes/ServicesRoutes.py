from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.Services import Services, ServicesUpdate
from app.models.Schedule import Schedule, ScheduleServices


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
    statement = select(Services)

    sercice = session.exec(statement).all()

    if not sercice:
        raise HTTPException(status_code=404, detail="Nenhum serviço cadastrado")
    
    services = (select(Services).offset(offset).limit(limit))
    return session.exec(services).unique().all()

@router.get("/{service_id}", response_model=Services)
def read_service_for_id(service_id: int, session: Session = Depends(get_session)):
    """Endpoint que reotrna um serviço a partir do id do serviço"""

    statement = select(Services).where(Services.id == service_id)

    service = session.exec(statement).first()

    if not service:
        raise HTTPException(status_code=404, detail=f"Serviço com o {service_id} não foi encontrado")
    
    return service


#  fazer verificação no schedule, se:
#  o schedule fica sem nenhum serviço, se o schedule não tiver mais nenhum serviço apos a remoção do serviço o schedule tem que ser deletado
@router.delete("/{service_id}")
def delete_service(service_id: int, session: Session = Depends(get_session)):
    """Endpoint que deleta o serviço a partir do id fornecido"""

    service = session.get(Services, service_id)

    if not service:
        raise HTTPException(status_code=404, detail=f"Serviço não foi encontrado")

    schedule_services  = session.exec(select(ScheduleServices).where(ScheduleServices.services_id == service.id)).all()

    # Mantém o controle dos schedules afetados
    affected_schedules = set()
    for schedule_service in schedule_services:
        affected_schedules.add(schedule_service.schedule_id)  # Rastreia os schedules relacionados
        session.delete(schedule_service)  # Remove as associações do serviço com o schedule

    
    session.delete(service)

    # Verifica os schedules que precisam ser apagados
    for schedule_id in affected_schedules:
        # Busca outros serviços associados ao schedule
        remaining_services = session.exec(select(ScheduleServices).where(ScheduleServices.schedule_id == schedule_id)).all()

         # Apaga o schedule se não houver mais serviços associados
        if not remaining_services:
            schedule = session.get(Schedule, schedule_id)
            session.delete(schedule)        

    session.commit()
    
    return {"ok": True}


@router.put("/{serice_id}", response_model=Services)
def update_service(service_id: int, serviceUpdate: ServicesUpdate, session: Session = Depends(get_session)):
    """Endpoint que realiza o update dos dados do serviço a partir do id repassado"""

    statement = select(Services).where(Services.id == service_id)

    service = session.exec(statement).first()

    if not service:
        raise HTTPException(status_code=404, detail=f"Serviço não foi encontrado")

    for key, value in serviceUpdate.model_dump(exclude_unset=True).items():
        setattr(service, key, value)

    session.add(service)
    session.commit()
    session.refresh(service)

    return service

