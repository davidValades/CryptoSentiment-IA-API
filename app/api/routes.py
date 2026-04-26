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

router = APIRouter()

@router.get(
    "/analyze/{ticker}", 
    response_model=SentimentResponse,
    summary="Analiza el sentimiento con memoria evolutiva",
    description="Ingiere datos de Binance y genera un feedback loop basado en el rendimiento pasado."
)
async def analyze_crypto_sentiment(
    ticker: str = Path(..., title="Símbolo del Ticker", examples=["BTC"], min_length=2, max_length=10),
    x_gemini_key: Optional[str] = Header(None, description="API Key provista por el cliente"),
    x_gemini_model: str = Header(settings.GEMINI_MODEL, description="Modelo provisto por el cliente")):
    
    # NUEVO: Sanitizamos el Ticker
    ticker_upper = ticker.upper().strip()
    
    # Si el usuario escribió "BTCUSDT", le quitamos el "USDT" para que quede solo "BTC"
    if ticker_upper.endswith("USDT"):
        ticker_upper = ticker_upper[:-4]
    
    try:
        # 1. Ingestión de Datos en Tiempo Real
        logger.info(f"Extrayendo métricas de mercado para {ticker_upper}...")
        binance_data = await BinanceClient.get_24h_ticker(ticker_upper)
        rsi_value = await BinanceClient.get_rsi_14d(ticker_upper)
        headlines = await NewsClient.get_latest_headlines(currency=ticker_upper, limit=15)
        fng_data = await FNGClient.get_sentiment()
        
        current_price = float(binance_data.get('last_price', 0))

        # 2. EL FEEDBACK LOOP (Memoria Episódica)
        logger.info(f"Consultando memoria de trading para {ticker_upper}...")
        history_context = DatabaseClient.get_trade_history_for_prompt(
            ticker=ticker_upper, 
            current_price=current_price
        )
            
        # 3. Procesamiento con IA Reflexiva
        logger.info(f"Enviando contexto y memoria a la IA ({x_gemini_model})...")
        analysis_result = await SentimentAgent.analyze_market_data(
            ticker=ticker_upper,
            binance_data=binance_data,
            rsi_value=rsi_value,
            headlines=headlines,
            fng_data=fng_data,
            trade_history_context=history_context,
            api_key=x_gemini_key,
            model_name=x_gemini_model
        )

        # 4. Persistencia y Trading Automático (¡AQUÍ ESTABA EL ERROR!)
        # Ahora llamamos a la nueva función que establece TP y SL automáticamente
        DatabaseClient.save_analysis_and_trade(
            ticker=ticker_upper,
            score=analysis_result.score,
            sentiment=analysis_result.sentiment,
            signal=analysis_result.action_signal,
            price=current_price
        )
        
        # Historial de scores para la gráfica del frontend
        analysis_result.history = DatabaseClient.get_history_scores(ticker_upper, limit=5)

        return analysis_result

    except Exception as e:
        logger.error(f"Error en el flujo de análisis para {ticker_upper}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno en el Oráculo: {str(e)}"
        )


# ==========================================
# RUTAS DE GESTIÓN DE BILLETERA
# ==========================================

@router.get("/wallet", summary="Obtiene el estado de la billetera y operaciones abiertas")
async def get_wallet():
    return DatabaseClient.get_wallet_info()


# ==========================================
# RUTAS DE GESTIÓN DE FUENTES (RSS)
# ==========================================

class SourceItem(BaseModel):
    url: str

@router.get("/sources")
async def get_rss_sources():
    return {"sources": NewsClient.get_sources()}

@router.post("/sources")
async def add_rss_source(source: SourceItem):
    actualizadas = NewsClient.add_source(source.url)
    return {"message": "Fuente añadida", "sources": actualizadas}

@router.delete("/sources")
async def remove_rss_source(source: SourceItem):
    actualizadas = NewsClient.remove_source(source.url)
    return {"message": "Fuente eliminada", "sources": actualizadas}