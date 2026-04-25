import httpx
import xml.etree.ElementTree as ET
import asyncio
import logging

logger = logging.getLogger(__name__)

class NewsClient:
    SOURCES = [
        "https://cointelegraph.com/rss",
        "https://cryptonews.com/news/feed/"
    ]

    @classmethod
    async def fetch_one_source(cls, url: str) -> list[str]:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = await client.get(url, headers=headers, timeout=5.0)
                root = ET.fromstring(response.text)
                return [item.find('title').text for item in root.findall('./channel/item') if item.find('title') is not None]
            except:
                return []

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[str]:
        # Ejecutamos todas las fuentes en paralelo
        tasks = [cls.fetch_one_source(url) for url in cls.SOURCES]
        results = await asyncio.gather(*tasks)
        
        # Aplanamos y filtramos
        all_headlines = [h for source_list in results for h in source_list]
        currency_upper = currency.upper()
        
        filtered = [h for h in all_headlines if currency_upper in h.upper()][:limit]
        return filtered