import logging
from fastapi import APIRouter, HTTPException, Path
from app.services.binance_client import BinanceClient
from app.services.news_client import NewsClient
from app.services.fng_client import FNGClient
from app.services.ai_agent import SentimentAgent
from app.models.sentiment import SentimentResponse

logger = logging.getLogger(__name__)

# Instanciamos el router
router = APIRouter()

@router.get(
    "/analyze/{ticker}", 
    response_model=SentimentResponse,
    summary="Analiza el sentimiento de una criptomoneda",
    description="Ingiere datos en tiempo real de Binance y CryptoPanic, y utiliza Gemini AI para emitir un veredicto de mercado."
)
async def analyze_crypto_sentiment(
    ticker: str = Path(..., title="Símbolo del Ticker", example="BTC", min_length=2, max_length=10)
):
    """
    Endpoint principal para obtener el análisis de sentimiento.
    """
    ticker_upper = ticker.upper()
    
    try:
        # 1. Ingesta de Datos (Podríamos usar asyncio.gather para hacerlas en paralelo y ganar milisegundos, 
        # pero secuencial es más seguro para debuggear en este MVP 1.0)
        logger.info(f"Obteniendo datos de Binance para {ticker_upper}...")
        binance_data = await BinanceClient.get_24h_ticker(f"{ticker_upper}USDT")
        
        logger.info(f"Obteniendo noticias RSS para {ticker_upper}...")
        headlines = await NewsClient.get_latest_headlines(currency=ticker_upper, limit=15)
        
        logger.info(f"Obteniendo datos del Fear & Greed Index para {ticker_upper}...")
        fng_data = await FNGClient.get_sentiment()

        headlines = await NewsClient.get_latest_headlines(currency=ticker_upper, limit=15)
        
        if not headlines:
            logger.warning(f"No se encontraron noticias recientes para {ticker_upper}.")
            
        # 2. Procesamiento con IA
        logger.info(f"Enviando contexto a Gemini para análisis...")
        analysis_result = await SentimentAgent.analyze_market_data(
            ticker=ticker_upper,
            binance_data=binance_data,
            headlines=headlines,
            fng_data=fng_data
        )
        
        # 3. Retorno de la respuesta validada
        return analysis_result

    except Exception as e:
        logger.error(f"Error en el flujo de análisis para {ticker_upper}: {str(e)}")
        # Envolvemos cualquier excepción interna en un error 500 estándar de FastAPI
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno procesando el oráculo para {ticker_upper}: {str(e)}"
        )