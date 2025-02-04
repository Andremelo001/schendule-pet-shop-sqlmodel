from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routes import ClientRoutes, PetRoutes, ScheduleRoutes, ServicesRoutes


# Configurações de inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# Inicializa o aplicativo FastAPI
app = FastAPI(lifespan=lifespan)

# Rotas para Endpoints
app.include_router(ClientRoutes.router)
app.include_router(PetRoutes.router)
app.include_router(ScheduleRoutes.router)
app.include_router(ServicesRoutes.router)
