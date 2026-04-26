import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import router as api_router
from app.services.db_client import DatabaseClient
from app.services.trading_engine import TradingEngine
from app.services.auto_pilot import AutoPilotEngine # <--- NUEVO

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ON STARTUP ---
    DatabaseClient.initialize_db()
    
    # 1. Arrancamos el Vigilante (Cierra operaciones)
    vigilante_task = asyncio.create_task(TradingEngine.start_engine())
    
    # 2. Arrancamos el Auto-Piloto (Abre operaciones, configurado a 4 horas)
    # Nota: Si quieres probarlo rápido, cámbialo a 0.05 (3 minutos)
    autopilot_task = asyncio.create_task(AutoPilotEngine.start_hunting(interval_hours=0.05))    
    yield
    
    # --- ON SHUTDOWN ---
    TradingEngine.stop_engine()
    AutoPilotEngine.stop_hunting()
    await vigilante_task
    await autopilot_task

app = FastAPI(
    title="🔮 CryptoSentiment AI Hedge Fund",
    lifespan=lifespan,
    version=settings.VERSION
)

app.include_router(api_router, prefix=settings.API_V1_STR, tags=["Oracle"])

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")