import httpx
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

class NewsClient:
    RSS_URL = "https://cointelegraph.com/rss"

    # Mapeo básico para buscar tanto el símbolo como el nombre completo
    COIN_NAMES = {
        "BTC": "BITCOIN",
        "ETH": "ETHEREUM",
        "SOL": "SOLANA",
        "XRP": "RIPPLE",
        "ADA": "CARDANO",
        "DOGE": "DOGECOIN",
        "DOT": "POLKADOT",
        "LTC": "LITECOIN",
        "RON": "RONIN"
    }

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[str]:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = await client.get(cls.RSS_URL, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                headlines = []
                
                currency_upper = currency.upper()
                full_name = cls.COIN_NAMES.get(currency_upper, "")

                for item in root.findall('./channel/item'):
                    title = item.find('title')
                    if title is not None and title.text:
                        # Convertimos el título a mayúsculas para hacer una búsqueda insensible a mayúsculas/minúsculas
                        title_upper = title.text.upper()
                        
                        # Filtro: Solo guardamos la noticia si menciona el Ticker o el Nombre Completo
                        if currency_upper in title_upper or (full_name and full_name in title_upper):
                            headlines.append(title.text)
                            
                    if len(headlines) >= limit:
                        break
                        
                return headlines
                
            except Exception as e:
                logger.error(f"Error de red al consultar RSS de noticias: {e}")
                raise Exception(f"No se pudieron obtener noticias: {str(e)}")