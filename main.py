from fastapi import FastAPI
from fastapi.responses import FileResponse # Importación nueva
from app.core.config import settings
from app.api.routes import router as api_router
from app.services.db_client import DatabaseClient


app = FastAPI(
    title="🔮 CryptoSentiment AI Oracle",
    description="API RESTful que actúa como Oráculo de mercado usando Google Gemini.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(api_router, prefix=settings.API_V1_STR, tags=["Sentiment Oracle"])
DatabaseClient.initialize_db()

# === ENDPOINT MODIFICADO ===
# Ahora la raíz sirve el archivo HTML
@app.get("/", tags=["UI"], summary="Carga la interfaz del Dashboard")
async def serve_frontend():
    return FileResponse("index.html")