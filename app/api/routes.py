import logging
from fastapi import APIRouter, HTTPException, Path, Header
from pydantic import BaseModel
from typing import Optional
from app.services.binance_client import BinanceClient
from app.services.news_client import NewsClient
from app.services.fng_client import FNGClient
from app.services.ai_agent import SentimentAgent
from app.models.sentiment import SentimentResponse
from app.services.db_client import DatabaseClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# Instanciamos el router
router = APIRouter()

@router.get(
    "/analyze/{ticker}", 
    response_model=SentimentResponse,
    summary="Analiza el sentimiento de una criptomoneda",
    description="Ingiere datos en tiempo real de Binance y fuentes RSS, y utiliza IA para emitir un veredicto de mercado."
)
async def analyze_crypto_sentiment(
    ticker: str = Path(..., title="Símbolo del Ticker", examples=["BTC"], min_length=2, max_length=10),
    x_gemini_key: Optional[str] = Header(None, description="API Key provista por el cliente"),
    x_gemini_model: str = Header(settings.GEMINI_MODEL, description="Modelo provisto por el cliente")):
    """
    Endpoint principal para obtener el análisis de sentimiento.
    """
    ticker_upper = ticker.upper()
    
    try:
        logger.info(f"Obteniendo datos de Binance para {ticker_upper}...")
        binance_data = await BinanceClient.get_24h_ticker(ticker_upper)
        
        logger.info(f"Calculando RSI de 14 días para {ticker_upper}...")
        rsi_value = await BinanceClient.get_rsi_14d(ticker_upper)
        
        logger.info(f"Obteniendo noticias RSS para {ticker_upper}...")
        headlines = await NewsClient.get_latest_headlines(currency=ticker_upper, limit=15)
        
        logger.info(f"Obteniendo datos del Fear & Greed Index para {ticker_upper}...")
        fng_data = await FNGClient.get_sentiment()
        
        logger.info(f"Buscando historial para {ticker_upper}...")
        previous_score = DatabaseClient.get_latest_score(ticker_upper)
        
        if not headlines:
            logger.warning(f"No se encontraron noticias recientes para {ticker_upper}.")
            
        # 2. Procesamiento con IA
        logger.info(f"Enviando contexto a la IA ({x_gemini_model}) para análisis...")
        analysis_result = await SentimentAgent.analyze_market_data(
            ticker=ticker_upper,
            binance_data=binance_data,
            rsi_value=rsi_value,
            headlines=headlines,
            fng_data=fng_data,
            previous_score=previous_score,
            api_key=x_gemini_key,
            model_name=x_gemini_model
        )

        DatabaseClient.save_score(ticker_upper, analysis_result.score)
        analysis_result.history = DatabaseClient.get_history(ticker_upper, limit=5)

        # 3. Retorno de la respuesta validada
        return analysis_result

    except Exception as e:
        logger.error(f"Error en el flujo de análisis para {ticker_upper}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno procesando el oráculo para {ticker_upper}: {str(e)}"
        )

# RUTAS DEL MODAL DE CONFIGURACIÓN

class SourceItem(BaseModel):
    url: str

@router.get("/sources", summary="Obtiene la lista de canales RSS activos")
async def get_rss_sources():
    return {"sources": NewsClient.get_sources()}

@router.post("/sources", summary="Añade un nuevo canal RSS")
async def add_rss_source(source: SourceItem):
    actualizadas = NewsClient.add_source(source.url)
    return {"message": "Fuente añadida", "sources": actualizadas}

@router.delete("/sources", summary="Elimina un canal RSS")
async def remove_rss_source(source: SourceItem):
    actualizadas = NewsClient.remove_source(source.url)
    return {"message": "Fuente eliminada", "sources": actualizadas}