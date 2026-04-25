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
                    "last_price": float(data.get("lastPrice", 0)),
                    "price_change_percent": float(data.get("priceChangePercent", 0)),
                    "volume_24h": float(data.get("volume", 0))
                }
            except Exception as e:
                logger.error(f"Error en Binance Client: {e}")
                raise e