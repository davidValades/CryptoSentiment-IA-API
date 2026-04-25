from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router as api_router

# Inicializamos la aplicación FastAPI con los metadatos de nuestra configuración
app = FastAPI(
    title="🔮 CryptoSentiment AI Oracle",
    description="""
    ### Bienvenido al Oráculo de Criptomonedas.
    Esta API analiza el pulso del mercado en tiempo real.
    
    * **Cuantitativo**: Precios y volumen desde Binance.
    * **Cualitativo**: Titulares de noticias de última hora.
    * **IA**: Cerebro basado en Gemini 2.0 Flash.
    """,
    version="1.0.0",
    contact={
        "name": "Soporte Técnico",
        "url": "https://tu-sitio.com",
    }
)

# Incluimos el router que acabamos de crear
app.include_router(api_router, prefix=settings.API_V1_STR, tags=["Sentiment Oracle"])

# Endpoint de Health Check (Buena práctica para DevOps/Docker)
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }