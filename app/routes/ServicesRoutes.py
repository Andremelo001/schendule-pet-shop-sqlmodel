from enum import Enum
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from app.database import get_session
from sqlalchemy import func
from app.models.Services import Services, ServicesUpdate
from app.models.Schedule import Schedule, ScheduleServices


class categoryPrice(str, Enum):
    cheap = "cheap services"
    medium = "medium services"
    expensive = "expensive services"


router = APIRouter(
    prefix="/services", 
    tags=["Services"],   
)

@router.post("/", response_model=Services)
def create_service(service: Services, session: Session = Depends(get_session)):
    """Endpoint para criar um novo serviço"""

    service_existing = session.exec(select(Services).where(Services.type_service == service.type_service)).first()

    if service_existing:
        raise HTTPException(status_code=400, detail=f"Serviço {service.type_service} já existe!")
    
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
    """Endpoint que retorna um serviço a partir de um `service_id` do serviço"""

    statement = select(Services).where(Services.id == service_id)

    service = session.exec(statement).first()

    if not service:
        raise HTTPException(status_code=404, detail=f"Serviço com o {service_id} não foi encontrado")
    
    return service


@router.delete("/{service_id}")
def delete_service(service_id: int, session: Session = Depends(get_session)):
    """Endpoint que deleta o serviço a partir de um `service_id` fornecido, 
    e caso o agendamento tenha o serviço que foi apagado, o agendamento é deletado caso não tenha mais nenhum serviço"""

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
    """Endpoint que realiza o update dos dados do serviço a partir do `service_id` repassado"""

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

@router.get("/category-price/", response_model=list[Services])
def get_services_by_category_price(category_price: categoryPrice, session: Session = Depends(get_session)):
    """
    Endpoint que retorna os serviços por uma categoria de preço, delimitada em: 
    serviços baratos(serviços que tem valor menor que R$50),
    serviços com preço medio(serviços que tem valor entre R$50 a R$100) e
    serviços caros(serviços que tem valor entre R$100 a R$150)
    """

    if category_price is categoryPrice.cheap:
        statement = select(Services).where(Services.price <= 50)
    
    elif category_price is categoryPrice.medium:
        statement = select(Services).where((Services.price > 50.0) & (Services.price <= 100.0))
    
    elif category_price is categoryPrice.expensive:
        statement = select(Services).where((Services.price > 100.0) & (Services.price <= 500.0))
    
    else:
        raise HTTPException(status_code=400, detail="Categoria de preço invalida")
    
    services = session.exec(statement).all()

    if not services:
        raise HTTPException(status_code=404, detail="Nenhum serviço encontrado na faixa de preço selecionada")

    return services

@router.get("/total-services/", response_model=int)
def get_total_services(session: Session = Depends(get_session)):
    """Endpoint que retorna a quantidade total de serviços cadastrados no sistema"""

    statement = select(func.count(Services.id))

    total_services = session.exec(statement).one()

    return total_services

    
