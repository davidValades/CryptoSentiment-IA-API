import httpx
import xml.etree.ElementTree as ET
import asyncio
import logging
import json
import os

logger = logging.getLogger(__name__)

class NewsClient:
    SOURCES_FILE = "sources.json"

    # Fuentes iniciales por defecto, se pueden modificar desde el modal de configuración
    DEFAULT_SOURCES = [
        "https://cointelegraph.com/rss",
        "https://cryptonews.com/news/feed/",
        "https://u.today/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://cryptoslate.com/feed/",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://finance.yahoo.com/news/rssindex"
    ]

    @classmethod
    def get_sources(cls) -> list[str]:
        """Carga las fuentes desde el JSON. Si no existe, lo crea con las default."""
        if not os.path.exists(cls.SOURCES_FILE):
            try:
                with open(cls.SOURCES_FILE, 'w') as f:
                    json.dump(cls.DEFAULT_SOURCES, f)
                return cls.DEFAULT_SOURCES
            except Exception as e:
                logger.error(f"Error creando {cls.SOURCES_FILE}: {e}")
                return cls.DEFAULT_SOURCES
            
        try:
            with open(cls.SOURCES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo {cls.SOURCES_FILE}: {e}")
            return cls.DEFAULT_SOURCES

    @classmethod
    def add_source(cls, url: str) -> list[str]:
        sources = cls.get_sources()
        if url not in sources:
            sources.append(url)
            with open(cls.SOURCES_FILE, 'w') as f:
                json.dump(sources, f)
        return sources

    @classmethod
    def remove_source(cls, url: str) -> list[str]:
        sources = cls.get_sources()
        if url in sources:
            sources.remove(url)
            with open(cls.SOURCES_FILE, 'w') as f:
                json.dump(sources, f)
        return sources

    @classmethod
    async def fetch_one_source(cls, url: str) -> list[str]:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = await client.get(url, headers=headers, timeout=8.0)
                root = ET.fromstring(response.text)
                return [item.find('title').text for item in root.findall('./channel/item') if item.find('title') is not None]
            except Exception as e:
                logger.warning(f"Error consultando fuente {url}: {e}")
                return []

    @classmethod
    async def get_latest_headlines(cls, currency: str = "BTC", limit: int = 15) -> list[str]:
        active_sources = cls.get_sources()
        
        tasks = [cls.fetch_one_source(url) for url in active_sources]
        results = await asyncio.gather(*tasks)
        
        all_headlines = [h for source_list in results for h in source_list]
        currency_upper = currency.upper()
        
        # Filtramos por el ticker
        filtered = [h for h in all_headlines if currency_upper in h.upper()][:limit]
        return filtered