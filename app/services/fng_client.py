import httpx
import logging

logger = logging.getLogger(__name__)

class FNGClient:
    URL = "https://api.alternative.me/fng/"

    @classmethod
    async def get_sentiment(cls) -> dict:
        """Obtiene el índice Fear & Greed actual."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(cls.URL, timeout=5.0)
                response.raise_for_status()
                data = response.json().get("data", [{}])[0]
                return {
                    "value": data.get("value", "50"),
                    "classification": data.get("value_classification", "Neutral")
                }
            except Exception as e:
                logger.warning(f"No se pudo obtener el F&G Index: {e}")
                return {"value": "50", "classification": "Neutral"}