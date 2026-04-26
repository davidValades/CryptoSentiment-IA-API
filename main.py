import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import router as api_router
from app.services.db_client import DatabaseClient
from app.services.trading_engine import TradingEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ON STARTUP ---
    DatabaseClient.initialize_db()
    # Arrancamos el motor de trading en segundo plano sin bloquear FastAPI
    engine_task = asyncio.create_task(TradingEngine.start_engine())
    yield
    # --- ON SHUTDOWN ---
    TradingEngine.stop_engine()
    await engine_task

app = FastAPI(
    title="🔮 CryptoSentiment AI Hedge Fund",
    lifespan=lifespan, # Inyectamos el ciclo de vida
    version=settings.VERSION
)

app.include_router(api_router, prefix=settings.API_V1_STR, tags=["Oracle"])

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")