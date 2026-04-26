import asyncio
import logging
from app.services.binance_client import BinanceClient
from app.services.db_client import DatabaseClient

logger = logging.getLogger(__name__)

class TradingEngine:
    _is_running = False

    @classmethod
    async def start_engine(cls):
        if cls._is_running:
            return
        cls._is_running = True
        logger.info("🚀 Motor de Trading (Vigilante) INICIADO.")
        
        while cls._is_running:
            try:
                # 1. Obtenemos las operaciones ABIERTAS
                open_trades = DatabaseClient.get_open_trades()
                
                for trade in open_trades:
                    trade_id, ticker, signal, entry_price, tp_price, sl_price = trade
                    
                    # 2. Consultamos el precio actual a Binance
                    ticker_data = await BinanceClient.get_24h_ticker(ticker)
                    current_price = float(ticker_data.get('last_price', 0))
                    
                    logger.debug(f"Vigilando {ticker}: Entrada=${entry_price} | Actual=${current_price} | TP=${tp_price} | SL=${sl_price}")
                    
                    # 3. Lógica de Ejecución (Cierre de posición)
                    close_trade = False
                    pnl_realized = 0.0
                    
                    if signal == "BUY":
                        if current_price >= tp_price:
                            close_trade, reason = True, "TAKE_PROFIT"
                        elif current_price <= sl_price:
                            close_trade, reason = True, "STOP_LOSS"
                    
                    elif signal == "SELL":
                        if current_price <= tp_price:
                            close_trade, reason = True, "TAKE_PROFIT"
                        elif current_price >= sl_price:
                            close_trade, reason = True, "STOP_LOSS"
                            
                    if close_trade:
                        # Calculamos PnL exacto
                        if signal == "BUY":
                            pnl_pct = (current_price - entry_price) / entry_price
                        else: # SELL
                            pnl_pct = (entry_price - current_price) / entry_price
                            
                        logger.info(f"⚡ OPERACIÓN CERRADA [{reason}]: {ticker} {signal} con {pnl_pct*100:.2f}% de PnL.")
                        DatabaseClient.close_trade(trade_id, current_price, pnl_pct)

            except Exception as e:
                logger.error(f"Error en el ciclo del Trading Engine: {e}")
                
            # Esperamos 10 segundos antes de volver a mirar el mercado
            await asyncio.sleep(10)

    @classmethod
    def stop_engine(cls):
        cls._is_running = False
        logger.info("🛑 Motor de Trading DETENIDO.")