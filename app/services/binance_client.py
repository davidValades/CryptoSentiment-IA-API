import httpx
import logging

# Inicializamos el logger
logger = logging.getLogger(__name__)

class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"

    # Diccionario de correcciones para Binance
    TICKER_FIXES = {
        "RON": "RONIN",
        "DOT": "DOT",  # Puedes añadir más excepciones aquí en el futuro
    }

    @classmethod
    async def get_24h_ticker(cls, symbol_input: str) -> dict:
        # 1. Limpiamos el input (quitamos USDT si el usuario lo mandó por error)
        clean_symbol = symbol_input.replace("USDT", "").upper()
        
        # 2. Aplicamos la corrección si existe (ej: RON -> RONIN)
        base_asset = cls.TICKER_FIXES.get(clean_symbol, clean_symbol)
        
        # 3. Construimos el par final
        final_symbol = f"{base_asset}USDT"
        
        url = f"{cls.BASE_URL}/ticker/24hr"
        params = {"symbol": final_symbol}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                
                # Manejamos el error 400 (Bad Request) de forma personalizada
                if response.status_code == 400:
                    raise Exception(f"El símbolo {final_symbol} no existe en Binance.")
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "symbol": data.get("symbol"),
                    "last_price": data.get("lastPrice", "0"),
                    "price_change_percent": data.get("priceChangePercent", "0"),
                    "volume_24h": float(data.get("quoteVolume", 0))
                }
            
    
            except Exception as e:
                logger.error(f"Error en Binance Client: {e}")
                raise e
            
    @classmethod
    async def get_rsi_14d(cls, symbol_input: str) -> float:
        """Calcula el RSI de 14 días usando las velas diarias de Binance"""
        clean_symbol = symbol_input.replace("USDT", "").upper()
        base_asset = cls.TICKER_FIXES.get(clean_symbol, clean_symbol)
        final_symbol = f"{base_asset}USDT"
        
        # Pedimos 15 velas diarias (klines) para tener 14 periodos de cambio
        url = f"{cls.BASE_URL}/klines"
        params = {"symbol": final_symbol, "interval": "1d", "limit": 15}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=5.0)
                if response.status_code != 200:
                    return 50.0 # Si falla, devolvemos 50 (Neutral) por seguridad
                    
                data = response.json()
                
                # Extraemos los precios de cierre (están en la posición 4 de cada vela)
                closes = [float(candle[4]) for candle in data]
                
                # Fórmula RSI
                gains, losses = [], []
                for i in range(1, len(closes)):
                    change = closes[i] - closes[i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                        
                avg_gain = sum(gains) / 14
                avg_loss = sum(losses) / 14
                
                if avg_loss == 0:
                    return 100.0 # Nadie vendió, avaricia total
                    
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
                return round(rsi, 2)
                
            except Exception as e:
                logger.warning(f"Error calculando RSI para {final_symbol}: {e}")
                return 50.0