import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CryptoPanicClient:
    BASE_URL = "https://cryptopanic.com/api/v1"

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[str]:
        """
        Obtiene los últimos titulares de noticias para una criptomoneda.
        """
        url = f"{cls.BASE_URL}/posts/"
        params = {
            "auth_token": settings.CRYPTOPANIC_API_KEY,
            "currency": currency.upper(),
            "kind": "news" # Solo queremos noticias reales, no medios o blogs sueltos
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Extraemos los resultados
                results = data.get("results", [])
                
                # Extraemos solo los títulos y limitamos a la cantidad solicitada (máx 15 para no saturar contexto de IA)
                headlines = [post.get("title") for post in results[:limit]]
                return headlines
                
            except httpx.HTTPError as e:
                logger.error(f"Error de red al consultar CryptoPanic para {currency}: {e}")
                raise Exception(f"No se pudieron obtener noticias de CryptoPanic: {str(e)}")