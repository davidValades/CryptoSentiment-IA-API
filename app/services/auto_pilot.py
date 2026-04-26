# app/services/auto_pilot.py
import asyncio
import logging
from app.services.binance_client import BinanceClient
from app.services.news_client import NewsClient # o CryptoPanicClient, el que prefieras
from app.services.fng_client import FNGClient
from app.services.ai_agent import SentimentAgent
from app.services.db_client import DatabaseClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class AutoPilotEngine:
    _is_running = False
    
    # Las monedas que el bot vigilará por ti mientras duermes
    TARGET_COINS = ["BTC", "ETH", "SOL"]

    @classmethod
    async def start_hunting(cls, interval_hours: float = 4.0):
        """Inicia el ciclo autónomo de búsqueda de oportunidades."""
        if cls._is_running:
            return
            
        cls._is_running = True
        interval_seconds = int(interval_hours * 3600)
        
        logger.info(f"🤖 AUTO-PILOTO INICIADO. Buscando oportunidades en {cls.TARGET_COINS} cada {interval_hours} horas.")

        # Esperamos 30 segundos tras arrancar el servidor antes de hacer la primera ronda
        await asyncio.sleep(30)

        while cls._is_running:
            try:
                for ticker in cls.TARGET_COINS:
                    logger.info(f"🔍 [AUTO-PILOTO] Escaneando {ticker}...")
                    
                    # 1. Recolección de Datos
                    binance_data = await BinanceClient.get_24h_ticker(ticker)
                    rsi = await BinanceClient.get_rsi_14d(ticker)
                    headlines = await NewsClient.get_latest_headlines(currency=ticker, limit=10)
                    fng = await FNGClient.get_sentiment()
                    
                    current_price = float(binance_data.get('last_price', 0))
                    
                    # Memoria de operaciones pasadas para que la IA aprenda
                    history = DatabaseClient.get_trade_history_for_prompt(ticker, current_price)

                    # 2. Análisis Cuantitativo de IA
                    analysis = await SentimentAgent.analyze_market_data(
                        ticker=ticker,
                        binance_data=binance_data,
                        rsi_value=rsi,
                        headlines=headlines,
                        fng_data=fng,
                        trade_history_context=history,
                        api_key=settings.GEMINI_API_KEY, # Usa la clave del servidor
                        model_name=settings.GEMINI_MODEL
                    )

                    # 3. Ejecución Autónoma
                    if analysis.action_signal in ["BUY", "SELL"]:
                        logger.info(f"⚡ [AUTO-PILOTO] Oportunidad encontrada: ¡Ejecutando {analysis.action_signal} en {ticker} a ${current_price:,.2f}!")
                        
                        # Esto guarda la operación en la DB y establece el TP/SL para que el Vigilante lo cierre luego
                        DatabaseClient.save_analysis_and_trade(
                            ticker=ticker,
                            score=analysis.score,
                            sentiment=analysis.sentiment,
                            signal=analysis.action_signal,
                            price=current_price
                        )
                    else:
                        logger.info(f"⏳ [AUTO-PILOTO] Mercado lateral o dudoso para {ticker}. Manteniendo HOLD.")
                        
                    # Pausa de 10 segundos entre monedas para no saturar las APIs ni a Gemini
                    await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error crítico en el ciclo del Auto-Piloto: {e}")
            
            # El bot se va a dormir hasta el próximo ciclo
            logger.info(f"💤 [AUTO-PILOTO] Ciclo terminado. Durmiendo por {interval_hours} horas...")
            await asyncio.sleep(interval_seconds)

    @classmethod
    def stop_hunting(cls):
        cls._is_running = False
        logger.info("🛑 AUTO-PILOTO DETENIDO.")